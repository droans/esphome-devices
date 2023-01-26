from functools import cached_property

import hassapi as hass

from shared_mods import LogWrapper
from dt import AppDT
from hass_const import(
    Domains,
    Services
)

class AppBase(hass.Hass):
    def init_base(self, logging_object, app_args = {}):
        self.__initialize_class__()

        logging = app_args.get('logging', {})
        log_level = logging.get('log_level', None)
        default_log_level = logging.get('default_log_level', None)
        self.SetLog(logger=logging_object, log_level=log_level, default_log_level=default_log_level)
        self.CheckEnabler(app_args)

    def __initialize_class__(self):
        self.DT = AppDT()
        self.Toggle = self.toggle
        self.State = self.get_state
        self.GetEntities = self.get_state

    def IsHome(self):
      return self.get_state('group.carrolls') == 'home'

    def GetDeviceEntities(self, device_id):
        template = f"device_entities('{device_id}')"
        template = "{{" + template + "}}"

        result = self.render_template(template)

        return result

    def GetDeviceID(self, entity_id):
        template = f'device_id("{entity_id}")'
        template = "{{" + template + "}}"

        result = self.render_template(template)

        return result

    def GetDeviceName(self, entity_id_or_device_id):
        if '.' in entity_id_or_device_id:
            device_id = self.GetDeviceID(entity_id_or_device_id)
        else:
            device_id = entity_id_or_device_id

        template = f'device_attr("{device_id}","identifiers")'
        template = "{{" + template + "}}"

        result = self.render_template(template)

        result = list(result)[0][0]

        return result

    @cached_property
    def _get_integrations(self):
        template_str = """
            {% set devs = states | map(attribute='entity_id') | map('device_id') | reject('eq', None) | unique | list %}
            {% set ns = namespace(ints=[]) %}
            {% for dev in devs %}
            {% set ids = (device_attr(dev, 'identifiers') | list) %}
            {% for id in ids %}
                {% set int_name = id[0] %}
                {% if int_name not in ns.ints %}
                {% set ns.ints = ns.ints + [int_name] %}
                {% endif %}
            {% endfor %}
            
            {% endfor %}
            {{ ns.ints }}
        """
        result = self.render_template(template_str)

    def IsDomain(self, entity, domain):
      return domain == entity.split('.')[0]


    def __entity_name_to_id(self, entity_name):
        e_id = f"input_boolean.{entity_name.replace(' ','_').lower()}"
        return e_id

    def __entity_id_to_name(self, entity_id):
        e_name = entity_id.split('.')[-1].replace('_',' ').title()
        

    def CheckEnabler(self, app_args):
        if 'app_toggle' in app_args:
            self.CreateEnabler(app_args)
            self.IsEnabled = self.Enabled

    def CreateEnabler(self, args = None, entity_name = None, entity_id = None):
        arg_name, arg_id = self._get_enabler_from_args(args)

        if arg_name != False:
            if entity_name is None:
                entity_name = arg_name
            if entity_id is None:
                entity_id = arg_id
        else:
            if entity_id is None and entity_name is None:
                raise ValueError(f'One of args, entity_name, or entity_id is required.')

            if entity_id is not None and entity_name is None:
                entity_name = self.entity_id_to_name(entity_id)
            
            elif entity_name is not None and entity_id is None:
                entity_id = self._entity_name_to_id(entity_name)

        attrs = {
            'friendly_name': entity_name,
            'unique_id': entity_id.split('.')[-1],
            'source': 'AppDaemon App Toggles'
        }
        
        self._exists_or_create(entity_id, 'on', attrs)
        self.Log(f'Created enabler entity {entity_id}', log_level = 5)
        self._enabler = entity_id
        return entity_id

    @property
    def Enabler(self):
        return self._enabler

    @Enabler.setter
    def Enabler(self, entity_id):
        if entity_id.split('.')[0] != 'input_boolean':
            entity_id = f"input_boolean.{entity_id.split('.')[-1]}"
        self._enabler = entity_id

    @property
    def Enabled(self):
        return self.get_state(self._enabler) == 'on'
    
    @Enabled.setter
    def Enabled(self, state):
        attr = self.get_entity('input_boolean.motion_garage').attributes
        self.set_state(entity, state=state, attributes=attr)

    def _exists_or_create(self, entity, state = 'on', attributes = None):
        # if self.get_state(entity) is None:
        #     if attributes is None:
        #         self.set_state(entity, state = state)
        #     else:
        #         self.set_state(entity, state = state, attributes = attributes)
        return

    def _get_enabler_from_args(self, args):
        enable_data = args.get('app_toggle', None)
        if enable_data is None:
            return False, False
        
        entity_id = enable_data.get('entity_id', None)
        entity_name = enable_data.get('entity_name', None)

        if entity_id is None and entity_name is None:
            return False, False

        if entity_id is None:
            entity_id = self._entity_name_to_id(entity_name)
        elif entity_name is None:
            entity_name = self.entity_id_to_name(entity_id)

        return entity_name, entity_id

    def SetLog(self, logger, log_level = 10, default_log_level = 10):
        logwrapper = LogWrapper(logger)

        logwrapper.SetLogLevel(log_level)
        logwrapper.SetDefaultLogLevel(default_log_level)

        self.Log = logwrapper.Log

    def __domain__(self, entity):
        return entity.split('.')[0]

    def TurnOn(self, entity,brightness=None):
      if self.__domain__(entity) == 'cover':
        self.Open(entity)
        return

      if brightness is not None and self.__domain__(entity) == "light":
        self.turn_on(entity, brightness=brightness)
      else:
        self.turn_on(entity)

    def TurnOff(self, entity):
      if self.__domain__(entity) == 'cover':
        self.Close(entity)
        return
      else:
        self.turn_off(entity)

    def Open(self, entity):
      self.call_service('cover/open_cover', entity_id=entity)

    def Close(self, entity):
      self.call_service('cover/close_cover', entity_id=entity)

