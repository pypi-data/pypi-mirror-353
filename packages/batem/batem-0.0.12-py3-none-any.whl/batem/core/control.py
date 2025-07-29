"""
This code is protected under GNU General Public License v3.0

A helper module dedicated to the design of time-varying state space model approximated by bilinear state space model.

Author: stephane.ploix@grenoble-inp.fr
"""
from __future__ import annotations
import numpy
import time
from abc import ABC, abstractmethod
from typing import Any
from enum import Enum
from datetime import datetime
from .components import Airflow
from .statemodel import StateModel
from .model import BuildingStateModelMaker
from .data import DataProvider
from .inhabitants import Preference


class VALUE_DOMAIN_TYPE(Enum):
    """An enum to define the type of the value domain of a control port"""
    CONTINUOUS = 0
    DISCRETE = 1


class AbstractModeFactory(ABC):

    def __init__(self, **provided_variables: dict[str, list[float]]) -> None:
        self.mode_variable_values: dict[str, list[float]] = provided_variables
        self.mode_variables: list[str] = list(self.mode_variable_values.keys())

    @abstractmethod
    def merge_to_mode(self, **variable_values) -> float:
        raise NotImplementedError("This method should be implemented in the child class")

    def __call__(self, k: int, **variable_values: dict[str, float]) -> dict[str, float]:
        mode_variable_values_k: dict[str, float] = {mode_variable: self.mode_variable_values[mode_variable][k] for mode_variable in self.mode_variables}  # get the values of the mode variables from the pre-existing series at time k
        for variable in variable_values:  # update the input data with the new provided values of the mode variables
            mode_variable_values_k[variable] = variable_values[variable]
        return self.merge_to_mode(**mode_variable_values_k)


class ModeFactory(AbstractModeFactory):

    def __init__(self, **provided_variables: dict[str, list[float]]) -> None:
        super().__init__(**provided_variables)
        if len(self.mode_variables) > 1:
            raise ValueError('ModeFactory should be used with a single mode variable')

    def merge_to_mode(self, **mode_variable_values_k: dict[str, float]) -> float:
        return int(mode_variable_values_k[self.mode_variables[0]] > 0)


class MultiplexModeFactory(AbstractModeFactory):

    def __init__(self, **provided_variables: dict[str, list[float]]) -> None:
        super().__init__(**provided_variables)

    def merge_to_mode(self, **mode_variable_values_k: dict[str, float]) -> float:
        return sum(2**i * int(mode_variable_values_k[self.mode_variables[i]] > 0) for i in range(len(self.mode_variables)))


class Port(ABC):

    def _intersection(self, *sets) -> tuple[float, float] | None:
        """Compute the intersection of two intervals.

        :param interval1: the first interval
        :type interval1: tuple[float, float]
        :param interval2: the second interval
        :type interval2: tuple[float, float]
        :return: the intersection of the two intervals
        :rtype: tuple[float, float] | None
        """
        if sets[0] is None:
            return None
        global_set: tuple[float, float] = sets[0]
        for _set in sets[1:]:
            if _set is None:
                return None
            else:
                if self.value_domain_type == VALUE_DOMAIN_TYPE.CONTINUOUS:
                    bound_inf: float = max(global_set[0], _set[0])
                    bound_sup: float = min(global_set[1], _set[1])
                    if bound_inf <= bound_sup:
                        global_set: tuple[float, float] = (bound_inf, bound_sup)
                    else:
                        return None
                else:
                    global_set: list[int] = list(set(global_set) & set(_set))
        return global_set
    
    def __union(self, *sets) -> tuple[float, float] | None:
        i = 0
        while i < len(sets) and sets[i] is None:
            i += 1
        if i == len(sets):
            return None
        global_set: tuple[float, float] = sets[i]
        i += 1
        while i < len(sets):
            if sets[i] is not None:
                if self.value_domain_type == VALUE_DOMAIN_TYPE.CONTINUOUS:
                    global_set: tuple[float, float] =(min(global_set[0], sets[i][0]), max(global_set[1], sets[i][-1]))
                else:
                    global_set: list[int] = list(set(global_set) | set(sets[i]))
            i += 1
        return tuple(global_set)

    def __init__(self, data_provider: DataProvider, variable_name: str, value_domain_type: VALUE_DOMAIN_TYPE, value_domain: list[float]) -> None:
        super().__init__()
        self.data_provider: DataProvider = data_provider
        self.variable_name: str = variable_name
        self.in_provider: bool = self._in_provider(variable_name)
        if self.in_provider:
            print(f'{variable_name} is saved automatically by the port')
        else:
            print(f'{variable_name} must be saved manually via the port at the end of a simulation')
        self.recorded_data: dict[int, float] = dict()
        self.value_domain_type: VALUE_DOMAIN_TYPE = value_domain_type
        self.modes_value_domains: dict[int, list[float]] = dict()
        if value_domain is not None:
            self.modes_value_domains[0] = value_domain

    def _in_provider(self, variable_name: str) -> bool:
        return self.data_provider is not None and variable_name in self.data_provider

    def __call__(self, k: int, port_value: float | None = None) -> list[float] | float | None:
        if port_value is None:
            if k in self.recorded_data:
                return self.recorded_data[k]
            else:
                return self.modes_value_domains[0]
        else:
            value_domain: list[float] = self._standardize(self.modes_value_domains[0])
            port_value = self._restrict(value_domain, port_value)
            self.recorded_data[k] = port_value
            if self.in_provider:
                self.data_provider(self.variable_name, k, port_value)
            return port_value
    
    def _restrict(self, value_domain: list[float], port_value: float) -> float:
        if self.value_domain_type == VALUE_DOMAIN_TYPE.DISCRETE:
            if port_value not in value_domain:
                distance_to_value = tuple([abs(port_value - v) for v in value_domain])
                port_value = value_domain[distance_to_value.index(min(distance_to_value))]
        else:
            port_value = port_value if port_value <= value_domain[1] else value_domain[1]
            port_value = port_value if port_value >= value_domain[0] else value_domain[0]
        return port_value

    def _standardize(self, value_domain: int | float | tuple | float | list[float]) -> None | tuple[float]:
        if value_domain is None:
            return None
        else:
            if self.value_domain_type == VALUE_DOMAIN_TYPE.DISCRETE:
                if type(value_domain) is int or type(value_domain) is float:
                    standardized_value_domain: tuple[int | float] = (value_domain,)
                if len(value_domain) >= 1:
                    standardized_value_domain = tuple(sorted(list(set(value_domain))))
            else:
                if type(value_domain) is not list and type(value_domain) is not tuple:
                    standardized_value_domain: tuple[float, float] = (value_domain, value_domain)
                else:
                    standardized_value_domain: tuple[float, float] = (min(value_domain), max(value_domain))
            return standardized_value_domain

    def save(self) -> None:
        if not self.in_provider:
            data = list()
            for k in range(len(self.data_provider)):
                if k in self.recorded_data:
                    data.append(self.recorded_data[k])
                else:
                    data.append(0)
            self.data_provider.add_external_variable(self.variable_name, data)
        else:
            if self.data_provider is None:
                raise ValueError('No data provider: cannot save the port data')
            else:
                print(f'{self.variable_name} is saved automatically')
                self.data_provider(self.variable_name, self.recorded_data)

    def __repr__(self) -> str:
        return f"Control port {self.variable_name}"

    def __str__(self) -> str:
        if self.value_domain_type == VALUE_DOMAIN_TYPE.DISCRETE:
            string = 'Discrete'
        else:
            string = 'Continuous'
        string += f" control port on {self.variable_name} with general value domain {self.modes_value_domains}"
        string += f", automatically recorded data: {self.in_provider}"
        return string


class ModePort(Port):
    """A control port that depends on a mode variable: the value domain is different depending on the mode.
    """

    def __init__(self, data_provider: DataProvider, variable_name: str, value_domain_type: VALUE_DOMAIN_TYPE, modes_value_domains: list[float], mode_factory: ModeFactory) -> None:
        super().__init__(data_provider, variable_name, value_domain_type, None)
        self.modes_value_domains = {mode: self._standardize(modes_value_domains[mode]) for mode in modes_value_domains}
        self.mode_factory: ModeFactory = mode_factory

    def value_domain(self, k: int, **mode_values: Any) -> list[float]:
        mode: dict[str, float] = self.mode_factory(k, **mode_values)
        return self.modes_value_domains[mode]

    def __call__(self, k: int, port_value: float | None = None, **mode_variable_values: dict[str, float]) -> list[float] | float | None:
        mode: dict[str, float] = self.mode_factory(k, **mode_variable_values)
        if port_value is None:
            return self.modes_value_domains[mode]
        else:
            port_value = self._restrict(self.modes_value_domains[mode], port_value)
            self.recorded_data[k] = port_value
            if self.in_provider:
                self.data_provider(self.variable_name, k, port_value)
            return port_value


class ContinuousPort(Port):
    def __init__(self, data_provider: DataProvider, variable_name: str, value_domain: list[float]) -> None:
        super().__init__(data_provider, variable_name, VALUE_DOMAIN_TYPE.CONTINUOUS, value_domain)


class DiscretePort(Port):
    def __init__(self, data_provider: DataProvider, variable_name: str, value_domain: list[float]) -> None:
        super().__init__(data_provider, variable_name, VALUE_DOMAIN_TYPE.CONTINUOUS, value_domain)


class ContinuousModePort(ModePort):
    def __init__(self, data_provider: DataProvider, variable_name: str, modes_value_domains: list[float], mode_factory: ModeFactory) -> None:
        super().__init__(data_provider, variable_name, VALUE_DOMAIN_TYPE.CONTINUOUS, modes_value_domains, mode_factory)


class DiscreteModePort(ModePort):
    def __init__(self, data_provider: DataProvider, variable_name: str, modes_value_domains: list[float], mode_factory: ModeFactory) -> None:
        super().__init__(data_provider, variable_name, VALUE_DOMAIN_TYPE.DISCRETE, modes_value_domains, mode_factory)


class ZoneTemperatureController:
    """A controller is controlling a power port to reach as much as possible a temperature setpoint modeled by a temperature port. The controller is supposed to be fast enough comparing to the 1-hour time slots, that its effect is immediate (level 0), or almost immediate (level 1, for modifying the next temperature).
    It would behave as a perfect controller if the power was not limited but it is.
    """

    def __init__(self, zone_temperature_name: str, zone_power_name: str, zone_heat_gain_name: str, hvac_power_port: ContinuousModePort, temperature_setpoint_port: DiscreteModePort) -> None:
        self.dp: DataProvider = temperature_setpoint_port.data_provider
        if zone_temperature_name not in self.dp:
            raise ValueError(f'{zone_temperature_name} is not in the data provider')
        self.zone_temperature_name: str = zone_temperature_name
        if zone_power_name not in self.dp:
            raise ValueError(f'{zone_power_name} is not in the data provider')
        self.zone_power_name: str = zone_power_name
        if zone_heat_gain_name not in self.dp:
            raise ValueError(f'{zone_heat_gain_name} is not in the data provider')
        self.zone_heat_gain_name: str = zone_heat_gain_name

        self.hvac_power_port: ContinuousModePort = hvac_power_port
        self.hvac_power_name: str = hvac_power_port.variable_name
        self.temperature_setpoint_port: DiscreteModePort = temperature_setpoint_port
        self.temperature_setpoint_name: str = temperature_setpoint_port.variable_name

        self._delay: int = None
        self.zone_power_name_index: int = None
        self.zone_temperature_name_index: int = None
        self.zone_input_names: list[str] = None
        self.zone_output_names: list[str] = None

    def _register_nominal_state_model(self, nominal_state_model: StateModel) -> None:
        """private method automatically by the manager to register a nominal state model to the controller.

        :param nominal_state_model: a nominal state model
        :type nominal_state_model: StateModel
        """
        self.zone_input_names: list[str] = nominal_state_model.input_names
        self.zone_output_names: list[str] = nominal_state_model.output_names
        if self.zone_power_name not in self.zone_input_names:
            raise ValueError(f'{self.zone_power_name} is not an input of the state model')
        if self.zone_temperature_name not in self.zone_output_names:
            raise ValueError(f'{self.zone_temperature_name} is not an output of the state model')

        self.zone_power_name_index: int = self.zone_input_names.index(self.zone_power_name)
        self.zone_temperature_name_index: int = self.zone_output_names.index(self.zone_temperature_name)
        D_condition: numpy.matrix = nominal_state_model.D[self.zone_temperature_name_index, self.zone_power_name_index]
        CB: numpy.matrix = nominal_state_model.C * nominal_state_model.B
        CB_condition: numpy.matrix = CB[self.zone_temperature_name_index, self.zone_power_name_index]
        if D_condition != 0:
            self._delay = 0
        elif CB_condition != 0:
            self._delay = 1
        else:
            raise ValueError(f'{self.zone_temperature_name} cannot be controlled by {self.hvac_power_name}')

    def delay(self) -> int:
        """Get the delay of the controller. 0 means that the controller reach the setpoint immediately, 1 means that the controller reach the setpoint with a delay of one time slot.

        :return: the delay of the controller
        :rtype: int 0 or 1
        """
        return self._delay

    def __repr__(self) -> str:
        """String representation of the controller.
        :return: a string representation of the controller
        :rtype: str
        """
        return self.hvac_power_name + '>' + self.zone_temperature_name

    def __str__(self) -> str:
        """String representation of the controller.
        :return: a string representation of the controller
        :rtype: str
        """
        string: str = f'{self.zone_temperature_name} is controlled by {self.hvac_power_port.variable_name}, contributing to {self.zone_power_name} at level {self._delay} thanks to the setpoint {self.temperature_setpoint_port.variable_name}'
        return string

    def compute_hvac_power_k(self, k, zone_temperature_setpoint_k, state_model_k: StateModel, state_k: numpy.matrix, inputs_k: dict[str, float], inputs_kp1: dict[str, float] = None) -> float:
        
        if zone_temperature_setpoint_k is None or numpy.isnan(zone_temperature_setpoint_k) or type(zone_temperature_setpoint_k) is float('nan'):
            return self.hvac_power_port(k, 0)
        
        zone_temperature_setpoint_k: float = self.temperature_setpoint_port(k, zone_temperature_setpoint_k)
        # inputs_k[self.zone_power_name] = self.hvac_power_port(k, inputs_k[self.zone_power_name])
        inputs_k[self.zone_power_name] = self.dp(self.zone_heat_gain_name, k)  # hvac_power_port(k, inputs_k[self.zone_power_name])
        
        U_k = numpy.matrix([[inputs_k[_]] for _ in self.zone_input_names])
        if self._delay == 0:
            hvac_power_k: numpy.matrix = (zone_temperature_setpoint_k - state_model_k.C[self.zone_temperature_name_index, :] * state_k - state_model_k.D[self.zone_temperature_name_index, :] * U_k) / state_model_k.D[self.zone_temperature_name_index, self.zone_power_name_index]
        elif self._delay == 1:
            if inputs_kp1 is None:
                raise ValueError("Inputs at time k and k+1 must be provided for level-1 controller {self.control_input_name} -> {self.controlled_output_name}")
            U_kp1 = numpy.matrix([[inputs_kp1[input_name]] for input_name in self.zone_input_names])
            hvac_power_k: numpy.matrix = (zone_temperature_setpoint_k - state_model_k.C[self.zone_temperature_name_index, :] * state_model_k.A * state_k - state_model_k.C[self.zone_temperature_name_index, :] * state_model_k.B * U_k - state_model_k.D[self.zone_temperature_name_index, :] * U_kp1) / (state_model_k.C[self.zone_temperature_name_index] * state_model_k.B[:, self.zone_power_name_index])
            hvac_power_k = hvac_power_k[0, 0]
        else:  # unknown level
            raise ValueError('No controller available')
        hvac_power_k = self.hvac_power_port(k, hvac_power_k)
        heat_gain_k = self.dp(self.zone_heat_gain_name, k)
        print(f'hvac_power_k: {hvac_power_k}')
        print(f'zone_heat_gain: {self.zone_heat_gain_name, heat_gain_k}')
        
        self.dp(self.zone_power_name, k, hvac_power_k + heat_gain_k)
        # return hvac_power_k


class ZoneManager(ABC):
    """A manager is a class that gathers all the data about a zone, including control rules.
    """

    def __init__(self, dp: DataProvider, zone_temperature_controller: ZoneTemperatureController, state_model_maker: BuildingStateModelMaker,  preference: Preference, initial_temperature: float = 20, **other_ports: Port) -> None:
        self.recorded_data: dict[str, dict[int, list[float]]] = dict()
        self.dp: DataProvider = dp
        self.zone_temperature_controller: ZoneTemperatureController = zone_temperature_controller
        self.preference: Preference = preference
        self.state_model_maker: BuildingStateModelMaker = state_model_maker
        self.nominal_state_model: StateModel = self.state_model_maker.make_nominal(reset_reduction=True)
        self.input_names: list[str] = self.nominal_state_model.input_names
        self.output_names: list[str] = self.nominal_state_model.output_names
        self.initial_temperature: float = initial_temperature
        self.datetimes: list[datetime] = self.dp.series('datetime')
        self.day_of_week: list[int] = self.dp('day_of_week')
        self.available_ports: dict[str, Port] = other_ports

        if self.zone_temperature_controller.zone_temperature_name not in self.output_names:
            raise ValueError(f'{self.zone_temperature_controller.zone_temperature_name} is not an output of the state model')
        self.zone_temperature_index: int = self.output_names.index(self.zone_temperature_controller.zone_temperature_name)
        self.preference: Preference = preference
        self.control_model: ControlModel = None
        
    def register_control_model(self, control_model: ControlModel) -> None:
        self.control_model = control_model

    def controls(self, k: int, X_k: numpy.matrix, current_output_dict: dict[str, float]) -> None:
        # if self.dp('presence', k) == 1:    ######### DESIGN YOUR OWN CONTROLS HERE #########
        #     self.window_opening_port(k, 1) # USE THE CONTROL PORTS FOR ACTION AND USE self.dp('variable', k) TO GET A VALUE
        pass

    def __str__(self) -> str:
        string: str = f"ZONE MANAGER\nBindings:\nzone_power == {self.zone_temperature_controller.zone_power_name}\nhvac_power == {self.zone_temperature_controller.hvac_power_port.variable_name}\nzone_temperature == {self.zone_temperature_controller.zone_temperature_name}\n"
        string += 'Nominal state model:\n'
        string += str(self.nominal_state_model) + '\n'
        string += str(self.preference)
        string += f'\nInitial temperature: {self.initial_temperature}\n'
        string += "Available ports:\n"
        for port_name in self.available_ports:
            # string += f"{self.available_ports[port_name]}\n"
            # string += f"{port_name} with type {type(self.available_ports[port_name])}\n"
            string += str(self.available_ports[port_name]) + '\n'
        return string


# class FedZoneManager(ZoneManager):
#     """A manager is a class that gathers all the data about a zone, including control rules.
#     """

#     def __init__(self, dp: DataProvider, zone_power_name: str, hvac_power_name: str, zone_temperature_name: str, state_model_maker: BuildingStateModelMaker, preference: Preference, initial_temperature: float = 20, **available_ports: Port) -> None:
#         super().__init__(dp, zone_power_name, hvac_power_name, zone_temperature_name, state_model_maker, preference, initial_temperature, **available_ports)


class ControlledZoneManager(ZoneManager):
    """A manager is a class that gathers all the data about a zone, including control rules.
    """

    def __init__(self, dp: DataProvider, zone_temperature_controller: ZoneTemperatureController, state_model_maker: BuildingStateModelMaker, preference: Preference, initial_temperature: float = 20, **other_ports: Port) -> None:
        super().__init__(dp, zone_temperature_controller, state_model_maker, preference, initial_temperature, **other_ports)

        self.available_set_points: bool = False
        self.zone_temperature_controller: ZoneTemperatureController = zone_temperature_controller
        self.has_controller: bool = zone_temperature_controller is not None
        self.available_set_points = False

        if self.has_controller:
            self.zone_temperature_controller: ZoneTemperatureController = zone_temperature_controller
            self.zone_temperature_controller._register_nominal_state_model(self.nominal_state_model)
            if self.zone_temperature_controller.zone_temperature_name not in self.output_names:
                raise ValueError(f'{self.zone_temperature_controller.zone_temperature_name} is not an output of the state model')
            if self.zone_temperature_controller.zone_power_name not in self.input_names:
                raise ValueError(f'{self.zone_temperature_controller.zone_power_name} is not an input of the state model')

            if self.zone_temperature_controller.temperature_setpoint_port.variable_name in self.dp:
                self.available_set_points = True
        else:  # no controller
            if self.zone_temperature_controller.temperature_setpoint_port.variable_name in self.dp:
                self.available_set_points = True
            else:
                raise ValueError(f'{self.zone_temperature_controller.temperature_setpoint_name} is not in the data provider')

    def state_model_k(self, k: int) -> StateModel:
        """Get the state model for time slot k.
        """
        return self.state_model_maker.make_k(k)

    def __str__(self) -> str:
        string: str = super().__str__()
        port: ContinuousModePort = self.zone_temperature_controller.hvac_power_port
        string += f'hvac_power_port on {port.variable_name} with type {type(port)}\n'
        string += str(port) + '\n'
        port = self.zone_temperature_controller.temperature_setpoint_port
        string += f'temperature_setpoint_port on {port.variable_name} with type {type(port)}\n'
        string += str(port) + '\n'
        return string
    

class ControlModel:
    """The main class for simulating a living area with a control.
    """

    def __init__(self, building_state_model_maker: BuildingStateModelMaker, manager: ControlledZoneManager = None) -> None:
        self.building_state_model_maker: BuildingStateModelMaker = building_state_model_maker
        self.dp: DataProvider = building_state_model_maker.data_provider
        self.airflows: list[Airflow] = building_state_model_maker.airflows
        self.fingerprint_0: list[int] = self.dp.fingerprint(0)  # None
        self.state_model_0: StateModel = building_state_model_maker.make_k(k=0, reset_reduction=True, fingerprint=self.fingerprint_0)
        self.input_names: list[str] = self.state_model_0.input_names
        self.output_names: list[str] = self.state_model_0.output_names
        self.state_models_cache: dict[int, StateModel] = {self.fingerprint_0: self.state_model_0}
        self.manager: ControlledZoneManager = manager
        if manager is not None:
            self.manager.register_control_model(self)

    def simulate(self, suffix: str = ''):
        print("simulation running...")
        start: float = time.time()
        # controller_controls: dict[str, list[float]] = {repr(self.manager.zone_temperature_controller): [self.manager.zone_temperature_controller]}  # list() for controller in self.manager.zone_temperature_controller}
        # controller_setpoints: dict[str, list[float]] = {repr(self.manager.zone_temperature_controller): [self.manager.zone_temperature_controller]}  # {repr(controller): list() for controller in self.manager.zone_temperature_controller}

        X_k: numpy.matrix = None
        counter = 0
        for k in range(len(self.dp)):
            current_outputs = None
            # compute the current state model
            current_fingerprint: list[int] = self.dp.fingerprint(k)
            if current_fingerprint in self.state_models_cache:
                state_model_k = self.state_models_cache[current_fingerprint]
                counter += 1
                if counter % 100 == 0:
                    print('.', end='')
            else:
                state_model_k: StateModel = self.building_state_model_maker.make_k(k, reset_reduction=(k == 0))
                self.state_models_cache[self.dp.fingerprint(k)] = state_model_k
                print('*', end='')
                counter = 0
            # compute inputs and state vector
            inputs_k: dict[str, float] = {input_name: self.dp(input_name, k) for input_name in self.input_names}
            if X_k is None:
                X_k: numpy.matrix = self.state_model_0.initialize(**inputs_k)
            # compute the output before change
            output_values: list[float] = state_model_k.output(**inputs_k)
            current_outputs: dict[str, float] = {self.output_names[i]: output_values[i] for i in range(len(self.output_names))}
            self.manager.controls(k, X_k, current_outputs)

            # compute the current state model after potential change by the "controls" function
            current_fingerprint: list[int] = self.dp.fingerprint(k)
            if current_fingerprint in self.state_models_cache:
                state_model_k = self.state_models_cache[current_fingerprint]
                counter += 1
                if counter % 100 == 0:
                    print('.', end='')
            else:
                state_model_k: StateModel = self.building_state_model_maker.make_k(k, reset_reduction=(k == 0))
                self.state_models_cache[self.dp.fingerprint(k)] = state_model_k
                print('*', end='')
                counter = 0
            # collect input data for time slot k (and k+1 if possible) from the data provided
            inputs_k: dict[str, float] = {input_name: self.dp(input_name, k) for input_name in self.input_names}
            if k < len(self.dp) - 1:
                inputs_kp1: dict[str, float] = {input_name: self.dp(input_name, k+1) for input_name in self.input_names}
            else:
                inputs_kp1 = inputs_k
            # update the input power value to reach the control temperature setpoints
            # for controller in self.manager.zone_temperature_controllers_initial_temperature:
            controller = self.manager.zone_temperature_controller
            controller_name: str = repr(controller)
            if controller._delay == 0:
                setpoint_k: float = self.dp(controller.zone_temperature_setpoint_variable, k)
                control_k: float = controller.compute_hvac_power_k(k, setpoint_k, state_model_k, X_k, inputs_k)
            elif controller._delay == 1:
                if k < len(self.dp) - 1:
                    setpoint_k: float = self.dp(controller.temperature_setpoint_port.variable_name, k+1)
                else:
                    setpoint_k: float = self.dp(controller.temperature_setpoint_port.variable_name, k)
            # control_k: float = controller.compute_hvac_power_k(k, setpoint_k, state_model_k, X_k, inputs_k, inputs_kp1)
            # controller_controls[controller_name].append(control_k)
            # controller_setpoints[controller_name].append(setpoint_k)

            # inputs_k[controller.zone_power_name] = inputs_k[controller.zone_power_name] + control_k
            # self.dp(controller.zone_power_name, k, control_k)

            state_model_k.set_state(X_k)
            output_values = state_model_k.output(**inputs_k)
            for output_index, output_name in enumerate(self.output_names):
                self.dp(output_name, k, output_values[output_index])
            X_k = state_model_k.step(**inputs_k)
        print(f"\nDuration in seconds {time.time() - start} with a state model cache size={len(self.state_models_cache)}")

    def __str__(self) -> str:
        string = 'ControlModel:'
        string += f'\n-{self.manager.zone_temperature_controller}'
        return string