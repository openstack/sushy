#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

from sushy.resources.chassis.power import constants as pow_cons

POWER_SUPPLY_TYPE_MAP = {
    'Unknown': pow_cons.POWER_SUPPLY_TYPE_UNKNOWN,
    'AC': pow_cons.POWER_SUPPLY_TYPE_AC,
    'DC': pow_cons.POWER_SUPPLY_TYPE_DC,
    'ACorDC': pow_cons.POWER_SUPPLY_TYPE_ACDC,
}

POWER_SUPPLY_INPUT_TYPE_MAP = {
    'AC': pow_cons.INPUT_TYPE_AC,
    'DC': pow_cons.INPUT_TYPE_DC,
}

LINE_INPUT_VOLTAGE_TYPE_MAP = {
    'Unknown': pow_cons.LINE_INPUT_VOLTAGE_TYPE_UNKNOWN,
    'ACLowLine': pow_cons.LINE_INPUT_VOLTAGE_TYPE_ACLOW,
    'ACMidLine': pow_cons.LINE_INPUT_VOLTAGE_TYPE_ACMID,
    'ACHighLine': pow_cons.LINE_INPUT_VOLTAGE_TYPE_ACHIGH,
    'DCNeg48V': pow_cons.LINE_INPUT_VOLTAGE_TYPE_DCNEG48,
    'DC380V': pow_cons.LINE_INPUT_VOLTAGE_TYPE_DC380,
    'AC120V': pow_cons.LINE_INPUT_VOLTAGE_TYPE_AC120,
    'AC240V': pow_cons.LINE_INPUT_VOLTAGE_TYPE_AC240,
    'AC277V': pow_cons.LINE_INPUT_VOLTAGE_TYPE_AC277,
    'ACandDCWideRange': pow_cons.LINE_INPUT_VOLTAGE_TYPE_ACDCWIDE,
    'ACWideRange': pow_cons.LINE_INPUT_VOLTAGE_TYPE_ACWIDE,
    'DC240V': pow_cons.LINE_INPUT_VOLTAGE_TYPE_DC240,
}
