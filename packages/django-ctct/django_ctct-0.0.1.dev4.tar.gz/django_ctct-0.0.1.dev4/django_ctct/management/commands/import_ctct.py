from argparse import ArgumentParser
from collections import defaultdict
from typing import Type, TypeVar, Optional, Any, Collection, Literal, cast
from uuid import UUID

from tqdm import tqdm

import django
from django.db.models import Model
from django.utils.translation import gettext as _
from django.core.management.base import BaseCommand

from django_ctct.models import (
  CTCTModel, CTCTEndpointModel, ContactList, CustomField,
  Contact, ContactCustomField,
  EmailCampaign, CampaignActivity, CampaignSummary,
  RelatedObjects, is_ctct
)
from django_ctct.utils import get_related_fields


M = TypeVar('M', bound=Model)
E = TypeVar('E', bound=CTCTEndpointModel, covariant=True)


class Command(BaseCommand):
  """Imports django-ctct model instances from CTCT servers.

  Notes
  -----
  CTCT does not provide an endpoint for fetching bulk CampaignActivities.
  As a result, we must loop through the EmailCampaigns, make a request to get
  the associated CampaignActivities, and then make a second request to get the
  details of the CampaignActivity.

  As a result, importing CampaignActivities will be slow, and running it
  multiple times may result in exceeding CTCT's 10,000 requests per day
  limit.

  """

  help = 'Imports data from ConstantContact'

  CTCT_MODELS: list[Type[CTCTEndpointModel]] = [
    ContactList,
    CustomField,
    Contact,
    EmailCampaign,
    CampaignActivity,
    CampaignSummary,
  ]

  def get_id_to_pk(
    self,
    model: Type[M] | Literal['self']
  ) -> dict[str, int]:
    """Returns a dictionary to convert CTCT API ids to Django pks."""
    if is_ctct(model):
      id_to_pk = {
        str(api_id): int(pk)
        for api_id, pk in model.objects.values_list('api_id', 'pk')
        if api_id is not None
      }
    else:
      id_to_pk = {}
    return id_to_pk

  def upsert(
    self,
    model: Type[M],
    objs: list[M],
    update_conflicts: bool = True,
    unique_fields: Optional[Collection[str]] = ['api_id'],
    update_fields: Optional[Collection[str]] = None,
    silent: Optional[bool] = None,
  ) -> list[Model]:
    """Perform upsert using `bulk_create()`."""

    verb = 'Imported' if (update_fields is None) else 'Updated'
    if silent is None:
      silent = self.noinput

    if model._meta.auto_created and hasattr(model, 'contactlist_id'):
      # Delete existing through model instances
      model.objects.all().delete()
      update_conflicts = False
      unique_fields = update_fields = None
    elif issubclass(model, ContactCustomField):
      update_conflicts = False
      unique_fields = update_fields = None
    elif issubclass(model, CampaignSummary):
      update_conflicts = True
      unique_fields = ['campaign_id']
      update_fields = model.API_READONLY_FIELDS[1:]
    elif update_fields is None:
      update_fields = [
        f.name
        for f in model._meta.fields
        if not f.primary_key and (f.name != 'api_id')
      ]

    # Remove possible duplicates (CTCT API can't be trusted)
    id_field: Optional[str] = None
    if model is CampaignSummary:
      id_field = 'campaign_id'
    elif issubclass(model, CTCTModel):
      id_field = 'api_id'

    if id_field is not None:
      seen, unique_objs = set(), []
      for obj in objs:
        if getattr(obj, id_field) not in seen:
          seen.add(getattr(obj, id_field))
          unique_objs.append(obj)
    else:
      unique_objs = objs

    # Perform the upsert
    objs_w_pks = model.objects.bulk_create(
      objs=unique_objs,
      update_conflicts=update_conflicts,
      unique_fields=unique_fields,
      update_fields=update_fields,
    )
    if update_conflicts and (django.get_version() < '5.0'):
      # In older versions, enabling the update_conflicts parameter prevented
      # setting the primary key on each model instance.
      if id_to_pk := self.get_id_to_pk(model):
        for o in filter(lambda o: o.api_id is not None, objs_w_pks):
          setattr(o, 'pk', id_to_pk[str(o.api_id)])

    # Inform the user
    if not silent:
      message = self.style.SUCCESS(
        f'{verb} {len(objs)} {model.__name__} instances.'
      )
      self.stdout.write(message)

    return objs_w_pks

  def set_direct_object_pks(
    self,
    model: Type[M],
    instances: list[M],
  ) -> None:
    """Sets Django pk values for OneToOne and ForeignKeys objects."""

    otos, _, fks, _ = get_related_fields(model)

    fields = otos + fks
    for field in fields:
      if id_to_pk := self.get_id_to_pk(field.related_model):
        for o in instances:
          setattr(o, field.attname, id_to_pk[str(getattr(o, field.attname))])

  def set_related_object_pks(
    self,
    model: Type[M],
    objs_w_pks: list[M],
    per_obj_list_of_related_objs: list[list[RelatedObjects]],
  ) -> None:
    """Sets Django pk values for ManyToMany and ReverseForeignKey objects."""

    if not any(per_obj_list_of_related_objs):
      return

    _, m2ms, _, rfks = get_related_fields(model)

    m2m_attnames = {
      field.remote_field.through: (
        field.m2m_column_name(), field.m2m_reverse_name()
      )
      for field in m2ms
    }
    if m2ms:
      id_to_pk = {
        m2m.remote_field.through: self.get_id_to_pk(m2m.related_model)
        for m2m in m2ms
      }

    rfk_attnames = {
      rel.related_model: rel.field.attname
      for rel in rfks
    }

    if model is Contact:
      # TODO: GH #14 ContactCustomField is kind of a ManyToMany
      m2m_attnames[ContactCustomField] = (
        rfk_attnames.pop(ContactCustomField), 'custom_field_id'
      )
      id_to_pk[ContactCustomField] = self.get_id_to_pk(CustomField)

    for obj_w_pk, list_of_related_objs in zip(objs_w_pks, per_obj_list_of_related_objs):  # noqa: E501
      for related_model, objs in list_of_related_objs:
        if m2m_attname := m2m_attnames.get(related_model):
          column_name, reverse_name = m2m_attname
          for o in objs:
            api_id = str(getattr(o, reverse_name))
            setattr(o, column_name, obj_w_pk.pk)
            setattr(o, reverse_name, id_to_pk[related_model][api_id])

        elif rfk_attname := rfk_attnames.get(related_model):
          for o in objs:
            setattr(o, rfk_attname, obj_w_pk.pk)

  def import_model(self, model: Type[E]) -> None:
    """Imports objects from CTCT into Django's database."""

    list_of_tuples: list[tuple[E, list[RelatedObjects]]]
    objs: list[E]
    per_obj_list_of_related_objs: list[list[RelatedObjects]]

    if model is CampaignActivity:
      # CampaignActivities do not have a bulk API endpoint
      return self.import_campaign_activities()

    model.remote.connect()
    try:
      # Split apart so we can save objs to db and get pks
      list_of_tuples = model.remote.all()
      objs, per_obj_list_of_related_objs = zip(*list_of_tuples)  # type: ignore[assignment]  # noqa: E501
    except ValueError:
      # No values returned
      return

    # Convert API id to Django pks
    self.set_direct_object_pks(model, objs)

    # Upsert models to get Django pks
    objs_w_pks = self.upsert(model, objs)

    # Convert API ids to Django pks for related objects
    self.set_related_object_pks(
      model,
      objs_w_pks,
      per_obj_list_of_related_objs,
    )

    # Reshape related_objs for efficiency
    dict_of_related_objs = defaultdict(list)
    for list_of_related_objs in per_obj_list_of_related_objs:
      for related_model, related_objs in list_of_related_objs:
        dict_of_related_objs[related_model].extend(related_objs)

    # Upsert related_obj_list
    for related_model, related_objs in dict_of_related_objs.items():
      self.upsert(related_model, related_objs)

  def import_campaign_activities(self) -> None:
    """CampaignActivities must be imported one at a time."""

    # First make sure CampaignActivity API id's are stored locally
    EmailCampaign.remote.connect()
    for campaign in EmailCampaign.objects.exclude(
      api_id__isnull=True,
      campaign_activities__role='primary_email',
      campaign_activities__api_id__isnull=False,
    ):
      # Fetch from API
      assert isinstance(campaign.api_id, UUID)
      try:
        _, list_of_related_objs = EmailCampaign.remote.get(campaign.api_id)
      except EmailCampaign.DoesNotExist:
        # Available in bulk endpoint but not detail endpoint
        continue
      else:
        # Set related object pk and store in db
        for related_model, objs in list_of_related_objs:
          if issubclass(related_model, CampaignActivity):
            for obj in cast(list[CampaignActivity], objs):
              if obj.role == 'primary_email':
                obj.campaign_id = campaign.pk
                obj.save()

    # Now fetch CampaignActivity details
    CampaignActivity.remote.connect()

    activities = CampaignActivity.objects.filter(
      role='primary_email',
      api_id__isnull=False,
    )

    objs_w_pks = []
    per_obj_list_of_related_objs = []

    for activity in tqdm(activities, disable=self.noinput):
      assert isinstance(activity.api_id, UUID)
      try:
        obj, list_of_related_objs = CampaignActivity.remote.get(activity.api_id)  # noqa: E501
      except CampaignActivity.DoesNotExist:
        # Came from EmailCampaign detail endpoint but doesn't exist elsewhere
        continue
      else:
        obj.pk = activity.pk
        obj.campaign_id = activity.campaign_id
        objs_w_pks.append(obj)
        per_obj_list_of_related_objs.append(list_of_related_objs)

    # Upsert objects to update fields
    self.upsert(
      model=CampaignActivity,
      objs=objs_w_pks,
      unique_fields=['campaign_id', 'role'],
      update_fields=['role', 'subject', 'preheader', 'html_content']
    )

    # Convert API id to Django pk for related objects
    self.set_related_object_pks(
      CampaignActivity,
      objs_w_pks,
      per_obj_list_of_related_objs,
    )

    # Reshape related_objs for efficiency
    dict_of_related_objs = defaultdict(list)
    for list_of_related_objs in per_obj_list_of_related_objs:
      for related_model, related_objs in list_of_related_objs:
        dict_of_related_objs[related_model].extend(related_objs)

    # Upsert related_obj_list
    for related_model, related_objs in dict_of_related_objs.items():
      self.upsert(related_model, related_objs)

  def add_arguments(self, parser: ArgumentParser) -> None:
    """Allow optional keyword arguments."""

    parser.add_argument(
      '--noinput',
      action='store_true',
      default=False,
      help='Automatic yes to prompts',
    )
    parser.add_argument(
      '--stats_only',
      action='store_true',
      default=False,
      help='Only fetch EmailCampaign statistics',
    )

  def handle(self, *args: Any, **kwargs: Any) -> None:
    """Primary access point for Django management command."""

    self.noinput = kwargs['noinput']
    self.stats_only = kwargs['stats_only']

    if self.stats_only:
      self.CTCT_MODELS = [CampaignSummary]

    for model in self.CTCT_MODELS:
      if model is CampaignActivity:
        note = "Note: This will result in 1 API request per EmailCampaign! "
      else:
        note = ""
      question = _(f'Import {model.__name__}? {note}(y/n): ')

      if self.noinput or (input(question).lower()[0] == 'y'):
        self.import_model(model)
      else:
        message = _(f'Skipping {model.__name__}')
        self.stdout.write(self.style.NOTICE(message))
