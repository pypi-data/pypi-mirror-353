from typing import Optional, Callable, Any, Dict, List, Set, OrderedDict
from copy import deepcopy
import numpy as np
from collections import OrderedDict as od
from code_loader.inner_leap_binder.inner_classes import FunctionType, TLFunction, MappingList
from code_loader.contract.datasetclasses import DatasetIntegrationSetup, VisualizerHandler, MetricHandler
from code_loader.contract.datasetclasses import DatasetBaseHandler, GroundTruthHandler, InputHandler


class LeapMapping:

    def __init__(self, setup_container: DatasetIntegrationSetup, mapping: MappingList):
        self.container : DatasetIntegrationSetup = setup_container
        self.mapping: MappingList = mapping
        self.max_id = 20000
        self.current_id = self.max_id
        self.mapping_json = []
        self.handle_dict = {
            FunctionType.gt : self.container.ground_truths,
            FunctionType.metric : self.container.metrics,
            FunctionType.visualizer: self.container.visualizers,
            FunctionType.input: self.container.inputs,
        }
        self.handle_to_op_type = {
            GroundTruthHandler: "GroundTruth",
            InputHandler: "Input",
            VisualizerHandler: "Visualizer"

        }
        self.function_to_json : Dict[TLFunction, List[Dict[str, Any]]] = {}

    def create_mapping_list(self, connections_list): #TODO add types
        pass

    def create_connect_nodes(self):
        for element in self.mapping:
            for sink in element.keys():
                for node_name, connected_func_list in element[sink].items():
                    tl_connected_functions = [ connected_func.tl_func for connected_func in connected_func_list
                                               if not isinstance(connected_func, int)]
                    for i, source in enumerate(tl_connected_functions):
                        print(sink, source, node_name)
                        sink_node = self.create_node(sink, name=node_name)
                        self.add_connections(sink_node, source, input_idx=i)
        print(1)
        import yaml
        with open('temp.yaml', 'w') as yf:
            yaml.safe_dump(({'decoder': self.mapping_json}), yf, default_flow_style=False, sort_keys=False)

    def create_partial_mapping(self): #TODO add types
        referenced = self._get_referenced_sinks()
        for func in referenced:
            kwargs = {}
            if func.FuncType == FunctionType.model_output:
                kwargs = {'name': func.FuncName}
            self.create_node(func, **kwargs)
        self.create_connect_nodes()

    def _get_referenced_sinks(self) -> Set[TLFunction]:
        referenced : Set[TLFunction] = set()
        references_types = {FunctionType.input, FunctionType.gt, FunctionType.model_output}
        for element in self.mapping:
            for func in element.keys():
                for node_name, connected_func_list in element[func].items():
                    tl_connected_functions = [ connected_func.tl_func for connected_func in connected_func_list
                                               if not isinstance(connected_func, int)]
                    for connected_func in tl_connected_functions:
                        if connected_func.FuncType in references_types:
                            referenced.add(connected_func)
        return referenced

    def create_gt_input(self, handle: DatasetBaseHandler, **kwargs) -> Dict[str, Any]:
        op_type = self.handle_to_op_type[type(handle)]
        json_node = {'operation': op_type,
                     'data': {'type': op_type, 'output_name': handle.name},
                     'id': f'{str(self.current_id)}',
                     'inputs': {},
                     'outputs': {handle.name: []}}
        return json_node

    def create_visualize(self, visualize_handle: VisualizerHandler ,**kwargs) -> Dict[str, Any]:
        op_type = "Visualizer"
        json_node = {'operation': op_type,
                     'data': {'type': op_type,
                              'name': visualize_handle.name,
                              'visualizer_name': visualize_handle.name,
                              'visualizer_type': visualize_handle.type.name,
                              'arg_names': deepcopy(visualize_handle.arg_names),
                              'user_unique_name': kwargs['name']},
                     'id': f'{str(self.current_id)}',
                     'inputs': {arg: [] for arg in visualize_handle.arg_names},
                     'outputs': {} }
        return json_node

    def create_metric(self, metric_handle: MetricHandler, **kwargs) -> Dict[str, Any]:
        op_type = "Metric"
        json_node = {'operation': op_type,
                     'data': {'type': op_type,
                              'name': metric_handle.name,
                              'metric_name': metric_handle.name,
                              'arg_names': deepcopy(metric_handle.arg_names),
                              'user_unique_name': kwargs['name']},
                     'id': f'{str(self.current_id)}',
                     'inputs': {arg: [] for arg in metric_handle.arg_names},
                     'outputs': {} }
        return  json_node


    def create_temp_model_node(self, node_type: TLFunction, **kwargs) -> Dict[str, Any]:
        default_name = self.get_default_name(node_type.FuncType, kwargs['name'])
        op_type = "PlaceHolder"
        json_node = {'operation': op_type,
                     'data': {'type': op_type,
                              'name': default_name,
                              'arg_names': [default_name],
                              'user_unique_name': default_name},
                     'id': f'{default_name}',
                     'inputs': {},
                     'outputs': {} }
        if node_type.FuncType == FunctionType.model_input:
            json_node['inputs'] = {default_name: []}
        else:
            json_node['outputs'] = {default_name: []}
        return json_node

    def _find_handle(self, node: TLFunction) -> DatasetBaseHandler:
        handle_list = self.handle_dict[node.FuncType]
        chosen_handle: Optional[DatasetBaseHandler] = None
        for handle in handle_list:
            if handle.name == node.FuncName:
                chosen_handle = handle
        assert chosen_handle is not None
        return chosen_handle

    def _find_json_node(self, node: TLFunction, **kwargs) -> Dict[str, Any]:
        candidates = self.function_to_json[node]
        if len(candidates) == 1:
            return candidates[0]
        elif len(candidates) > 1:
            raise Exception("More than 1 candidate - solve")
        else:
            raise Exception(f"No json node creted for node {node}")

    def _get_node_id(self, node: TLFunction, **kwargs):
        node = self._find_json_node(node, **kwargs)
        return node['id']

    def create_node(self, node_type: TLFunction, **kwargs) -> Dict[str, Any]:
        if node_type.FuncType in [FunctionType.model_output, FunctionType.model_input]:
            json_node = self.create_temp_model_node(node_type, **kwargs)
        else:
            node_creator_map: Dict[FunctionType, Callable[..., Any]] = { FunctionType.gt : self.create_gt_input,
                                                                         FunctionType.input: self.create_gt_input,
                                                                         FunctionType.visualizer: self.create_visualize,
                                                                         FunctionType.metric: self.create_metric}
            handle = self._find_handle(node_type)
            json_node = node_creator_map[node_type.FuncType](handle, **kwargs)
            self.current_id += 1
        self.function_to_json[node_type] =  self.function_to_json.get(node_type, []) + [json_node]
        self.mapping_json.append(json_node)
        return  json_node

    def get_default_name(self, f_type: FunctionType, name: str):
        return f"{str(f_type)}_{name}"

    def _get_node_output_name(self, node: TLFunction):
        if node.FuncType not in {FunctionType.model_output, FunctionType.model_input}:
            from_handle = self._find_handle(node)
            output_name = from_handle.name
        else:
            output_name = self.get_default_name(node.FuncType, node.FuncName)
        return output_name


    def add_connections(self, to_json: Dict[str, Any], from_node: TLFunction, input_idx: int):
        try:
            input_name = to_json['data']['arg_names'][input_idx]
        except Exception as e:
            raise Exception(f"arg names mismatch when adding input for {to_json['operation']}")
        output_key = self._get_node_output_name(from_node)
        from_json = self._find_json_node(from_node)
        operation = from_json['operation']
        from_id = from_json['id']
        # Add Input
        to_json['inputs'][input_name].append({'outputKey': output_key,
                                              'operation': operation,
                                              'id': from_id
                                              })
        # Add Output
        from_json['outputs'][output_key].append({'inputKey': input_name,
                                              'operation': to_json['operation'],
                                              'id': to_json['id']
                                              })

    def add_output(self, input_node, output_node):
        pass

def create_mapping(model_parser_map, connections_list):

    referenced_gt = []
    referenced_inputs = []
    for element in connections_list:
        for func in element.keys():
            for node_name, connected_func_list in element[func].items():
                tl_connected_functions = [ connected_func.tl_func if not isinstance(connected_func, int) else connected_func
                                      for connected_func in connected_func_list ]





    # Check Max Node ID
    # Get Preds Node ID

    # TODO Create Inputs (if referenced)
    # TODO Create Gts (if referenced)
    # TODO Create Visualizers
    # TODO Create Metrics
    # TODO Create losses
