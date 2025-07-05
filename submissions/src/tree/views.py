from dataclasses import dataclass,field

@dataclass
class TreeState:
    interactive_nodes:list['TreeElementNode']=field(default_factory=[])
    informative_nodes:list['TextElementNode']=field(default_factory=[])

    def interactive_elements_to_string(self)->str:
        return '\n'.join([f'Label: {index} App Name: {node.app_name} ControlType: {f'{node.control_type} Control'} Name: {node.name} Shortcut: {node.shortcut} Cordinates: {node.center.to_string()}' for index,node in enumerate(self.interactive_nodes)])
    
    def informative_elements_to_string(self)->str:
        return '\n'.join([f'Label: {index} App Name: {node.app_name} Name: {node.name}' for index,node in enumerate(self.informative_nodes)])



@dataclass
class Center:
    x:int
    y:int

    def to_string(self)->str:
        return f'({self.x},{self.y})'

@dataclass
class TreeElementNode:
    name:str
    control_type:str
    shortcut:str
    center:Center
    app_name:str

@dataclass
class TextElementNode:
    name:str
    app_name:str