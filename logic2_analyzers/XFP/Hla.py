import sys

sys.path.insert(0, "../") # our fake sigrokdecode lives one dir upper

from pd import Decoder

class XFP():
  def __init__(self):
    self.sigrokDecoder = Decoder()

  def get_capabilities(self):
    settings =  {}
    for option in self.sigrokDecoder.options :
        settingType = ''
        choices = []
        if ("values" not in option) :
            # TODO sigrok docs does not mention that default is mandatory
            if (isinstance(option['default'], str)) :
                settingType = 'string'
            elif (isinstance(option['default'], int) or isinstance(option['default'], float)) :
                settingType = 'number'
            else :
                print("Cannot determine the type of the  " + option['desc'] + " parameter from it's default value: " + option['default'])
        settings[option["desc"]] = {
            'type': settingType
        }
        if ("values" in option) :
            settings[option["desc"]]['choices'] = option["values"]
    return {
        'settings': settings
    }

  def set_settings(self, settings):
    # TODO handle the settings

    # convert sigrok's
    # annotations = (
    #    ('warning', 'Warning'),
    #    ....
    #
    # format annotations to Logic's format
    self.sigrokDecoder.reset()
    resultTypes = {}
    for annotation in self.sigrokDecoder.annotations :

        resultTypes[annotation[0]] = annotation[1] + "{{data.data}}"

    return {
        "result_types": resultTypes
    }

  def decode(self, data):
    self.sigrokDecoder.processI2C(data)
    if (not self.packet == {}) :
        ret = self.generate_logic_result()
        self.packet = {}
        return ret