from app_base import AppBase
from datetime import datetime
import time

class CalendarEvents(AppBase):
    def initialize(self):
        self.initialize_class()

    def initialize_class(self):
        self.init_base(self.log, self.args)
        self.Log(f'{self.args}', log_level = 5)

        self.__get_new_sensor_data__()
        self.__get_event_data__()
        self.ProcessSensors()
        self.__generate_callbacks__()

    def __get_event_data__(self):
        event_data = self.args.get('events')

        self.Log(f'Event data received: {event_data}', log_level = 5)

        sensors = event_data['sensors']
        attributes = event_data['attributes']

        self.__sensors__ = sensors

        self.Log(f'Received sensors {sensors}', log_level = 2)

        self.__name_attr__ = attributes['name']

        self.__start_attr__ = attributes['start']

        if 'end' in attributes:
            self.__end_attr__ = attributes['end']
        else:
            self.__end_attr__ = self.__start_attr__

        return

    def __generate_callbacks__(self):
        callback_timer = self.args.get('update_interval', 120)

        self.Log(f'Calling for a sensor update every {callback_timer} seconds.', log_level = 5)

        now = datetime.now()
        self.run_every(self.ProcessSensors, start = now, interval = callback_timer)

    def __get_new_sensor_data__(self):
        new_sensor_data = self.args.get('updated_sensors')

        name_template = new_sensor_data['name_template']

        sensor_count = new_sensor_data['total_sensors']

        self.__updated_sensors__ = []

        for i in range(1, sensor_count + 1):
            new_entity = name_template.replace('{id}', str(i))
            self.Log(f'New sensor entity: {new_entity}', log_level = 2)

            sensor_cur_state = self.get_state(new_entity)

            if sensor_cur_state is None:
                self.Log(f'Creating sensor {new_entity} as it does not yet exist.', log_level = 8)

                self.get_entity(new_entity).set_state(state='unknown')

            self.__updated_sensors__.append(new_entity)

    def __trim_sensor_data__(self, trim_data):
        new_sensors = self.args.get('updated_sensors')
        trim_len = -1

        if 'trim' in new_sensors:
            trim_len = new_sensors['trim']

            self.Log(f'Current sensor data: {trim_data}', log_level = 4)

            if len(trim_data) > trim_len:

                trim_data = trim_data[:trim_len] + '...'

            else:
                pass

        return trim_data

    def GetEventName(self, sensor):
        attr_name = self.__name_attr__
        event_name = self.get_state(sensor, attribute=attr_name)

        return event_name

    def GetEventStart(self, sensor):
        attr_start = self.__start_attr__

        start_ts = self.__get_timestamp_from_template__(sensor, attr_start)

        return start_ts

    def GetEventEnd(self, sensor):
        attr_end = self.__end_attr__

        end_ts = self.__get_timestamp_from_template__(sensor, attr_end)

        return end_ts

    def ProcessSensors(self, *args):

        valid_sensors = []
        now_ts = datetime.now().timestamp()

        for item in self.__sensors__:
          self.Log(f'{item}', log_level = 5)
          cal_name = item['name']
          for sensor in item['sensors']:
            sensor_name = self.GetEventName(sensor)
            e_name = self.GetEventName(sensor)

            if sensor_name is None:
              continue
            event_name = cal_name + ': ' + e_name
            event_name = self.__trim_sensor_data__(event_name)

            start = self.GetEventStart(sensor)
            end = self.GetEventEnd(sensor)

            if start is not None and start > now_ts:
              self.Log(f'Start time for {event_name} after now. Adding', log_level = 8)
              cur_item = {}
              cur_item['event'] = event_name
              cur_item['message'] = self.CreateTimeString(start)
              cur_item['start_timestamp'] = start
              cur_item['end_timestamp'] = end
              valid_sensors.append(cur_item)

        self.UpdateSensors(valid_sensors)

    def NewProcessSensors(self, *args):
        attr_name = self.__name_attr__

        attr_start = self.__start_attr__

        attr_end = self.__end_attr__

        valid_sensors = []
        now_ts = datetime.now().timestamp()

        self.Log(f'Sensors: {self.__sensors__}', log_level=2)

        for item in self.__sensors__:
            self.Log(f'Sensor state: {self.get_state("sensor.ical_michael_google_calendar_event_0")}')
            event_name = self.get_state(item, attribute=attr_name)

            self.Log(f'Event sensor: {item}, event data: {event_name}', log_level = 4)

            event_name = self.__trim_sensor_data__(event_name)

            self.Log(f'Event received: {event_name}', log_level = 4)

            event_start = self.get_state(item, attribute = attr_start)

            self.Log(f'Start time: {event_start}', log_level = 2)


            event_end = self.get_state(item, attribute = attr_end)

            self.Log(f'End time: {event_end}', log_level = 2)

            start_ts = self.__get_timestamp_from_template__(item, attr_start)
            end_ts = self.__get_timestamp_from_template__(item, attr_end)

            self.Log(f'Start time as timestamp: {start_ts}', log_level = 5)
            self.Log(f'End time as timestamp: {end_ts}', log_level = 5)

            if start_ts > now_ts:
                self.Log(f'Start time for {item} is greater than now. Adding...', log_level = 8)
                cur_item = {}
                cur_item['event'] = event_name
                cur_item['message'] = self.CreateTimeString(start_ts)
                cur_item['start_timestamp'] = start_ts
                cur_item['end_timestamp'] = end_ts
                valid_sensors.append(cur_item)
            else:
                self.Log(f'Start time for {item} is before now. Not adding...', log_level = 8)

        self.UpdateSensors(valid_sensors)

    def UpdateSensors(self, valid_sensors):
        timestamps = []
        ts_dict = {}

        for item in valid_sensors:
            start_ts = item['start_timestamp']
            ts_dict[start_ts] = item
            timestamps.append(start_ts)

        timestamps.sort()


        new_sensor_data = self.__updated_sensors__
        sensor_ct = len(new_sensor_data)

        allowed_sensors = timestamps[:sensor_ct]

        self.Log(f'New sensor data: {new_sensor_data}', log_level = 5)

        for i in range(sensor_ct):
            ts = allowed_sensors[i]
            new_sensor = new_sensor_data[i]

            new_data = ts_dict[ts]

            self.Log(f'Current sensor data: {new_data} for new sensor {new_sensor}', log_level = 4)

            self.get_entity(new_sensor).set_state(state = new_data['event'], attributes = {'message': new_data['message']})



    def CreateTimeString(self, time):
        min_divisor = 60
        hr_divisor = 3600
        day_divisor = 86400
        week_divisor = 604800

        now = datetime.now().timestamp()

        if type(time) is not float:
            if type(time) is datetime:
                time = time.timestamp()

        time_dif = time - now 

        if time_dif < hr_divisor:
            ts = 'Minute'
            divisor = min_divisor   
        elif time_dif < day_divisor:
            ts = 'Hour'
            divisor = hr_divisor
        elif time_dif < week_divisor:
            ts = 'Day'
            divisor = day_divisor
        else:
            ts = 'Week'
            divisor = week_divisor

        dif = int(round(time_dif / divisor, 0))

        dt = datetime.fromtimestamp(time)

        dt_str = dt.strftime(' (%a %-m/%-d %-I:%M %p)')

        self.Log(f'Datetime string: {dt_str}', log_level = 3)

        if dif != 1:
            ts = ts + 's'
        
        msg = 'In ' + str(dif) + ' ' + ts + dt_str
        
        self.Log(f'Message to return: {msg}', log_level = 3)
        
        return msg
            

    def __get_timestamp_from_template__(self, entity, attribute):
        template = "{{ as_timestamp(state_attr('" + entity + "','" + attribute + "')) }}"

        return self.render_template(template)

    def GetSensors(self):
        pass
