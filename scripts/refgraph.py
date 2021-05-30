import sys
import subprocess
import os
import json
import pandas as pd
import networkx as nx
import io
from graphviz import Digraph

from scripts.catalog import Catalog

class RefactoringGraph:

    def extract_graph(self, language, refactorings):
        node_id = 0
        edge_id = 0
        nodes = {}
        edges = {}
        
        for index, ref in refactorings.iterrows():

            entity_before = ref.get('entityBeforeFullName')
            entity_after = ref.get('entityAfterFullName')

            if entity_before not in nodes: 
                nodes[entity_before] = node_id
                node_id += 1
            
            if entity_after not in nodes: 
                nodes[entity_after] = node_id
                node_id += 1     
            
            #Edges properties
            edge = {}

            for key in ref.keys():
                edge[key] = ref.get(key)

            edge['nodeBeforeId'] = nodes.get(entity_before)
            edge['nodeAfterId'] = nodes.get(entity_after)
            edge['edgeId'] = edge_id
            edge['refactoringCode'] = Catalog.operations(language).get(ref.get('refactoringType'))

            edge_key = '{}_{}'.format(edge.get('nodeBeforeId'), edge.get('nodeAfterId'))
            
            if edge_key not in edges:
                edges[edge_key] = [] #Iniatize new edge
                edges[edge_key].append(edge)#Including new refactoring
                edge_id += 1  # update edge number

        return {'nodes': nodes, 'edges': edges}

    def create_digraph(self, data):
    
        DG = nx.DiGraph()
        
        nodes = data['nodes']
        edges = data['edges']
        
        #Adding nodes
        for entity in nodes:
            node_index = nodes[entity]
            DG.add_node(node_index)
        
        #Adding edges
        for key in edges:
            list_edges = edges[key]
            for edge in list_edges:#arestas no mesmo sentido.
                DG.add_edge(edge['nodeBeforeId'], edge['nodeAfterId'])
        
        return {'digraph': DG}


    def get_edges_by_nodes(self, node_number_1, node_number_2, graph_data):
    
        edges = graph_data['edges']
        edges_selected = []
        
        #loooking for edges in the directed graph
        edge_key_1 = '{}_{}'.format(node_number_1, node_number_2)
        edge_key_2 = '{}_{}'.format(node_number_2, node_number_1)
        
        if edge_key_1 in edges:
            edges_selected.append(edges[edge_key_1])
            
        if (edge_key_2 in edges) and (edge_key_1 != edge_key_2):#para arestas entrando e saindo do mesmo vertice
            edges_selected.append(edges[edge_key_2])
            
        return {'edges': edges_selected}

    def extract_subgraphs(self, project, digraph, graph_data):
    
        directed_subgraphs = []
        
        # undirected digraph
        UG = digraph.to_undirected()

        # extract subgraphs
        subgraphs = nx.connected_component_subgraphs(UG)

        #create transactions
        for i, subgraph in enumerate(subgraphs):
            
            directed_subgraph  = {}
            directed_subgraph['id'] = i
            directed_subgraph['project'] = project
            
            #add nodes
            nodes = []
            nodes.extend(subgraph.nodes())
            directed_subgraph['nodes'] = nodes
            
            #add adges
            edges = []
            
            for edge in subgraph.edges():
                node_number_1 = edge[0]
                node_number_2 = edge[1]
                directed_edges = self.get_edges_by_nodes(node_number_1, node_number_2, graph_data)['edges']
                edges.extend(directed_edges)

            directed_subgraph['edges'] = edges
            
            directed_subgraphs.append(directed_subgraph)
            
        #for i, sg in enumerate(subgraphs):
        #    print ("subgraph {} has {} nodes".format(i, sg.number_of_nodes()))
        #    print ("\tNodes:", sg.nodes(data=True))
        #    print ("\tEdges:", sg.edges(data=True))
        return {'directed_subgraphs': directed_subgraphs}

    def contains_different_commits(self, subgraph):
        edges = subgraph['edges']
        list_commits = []
        for edge in edges:
            for refactoring in edge:
                commit = refactoring['commitHash']
                if (len(list_commits) > 0) and (commit not in list_commits): #is a new and different commit
                    return True
                list_commits.append(commit)
        return False
    
    def split_supgraphs_atomic_and_overtime(self, subgraphs):
        subgraphs_same_commit = []
        subgraphs_different_commit = []
        for subgraph in subgraphs:
            subgraph_contains_different_commits = self.contains_different_commits(subgraph)
            if subgraph_contains_different_commits:
                subgraph['labelGroup'] = 'overtime' 
                subgraphs_different_commit.append(subgraph)
            else:
                subgraph['labelGroup'] = 'atomic' 
                subgraphs_same_commit.append(subgraph)
        return {'atomic': subgraphs_same_commit, 'overtime': subgraphs_different_commit}

    def write_json(self, file_json, path, file_name):
        if os.path.isfile(os.path.join(path, file_name)):
            print('ERRO: File exists %s' % os.path.join(path, file_name))
        else:
            if not os.path.exists(path):
                os.makedirs(path)
            file = open(os.path.join(path, file_name), 'w+')
            print('Creating %s ' % os.path.join(path, file_name))
            json.dump(file_json, file)
            file.close()
        return

    def find_disconnected_subgraphs(self, project, language):

        refactorings = pd.read_csv('dataset/{}/results/selected_refactorings.csv'.format(project), sep=';', keep_default_na=False)

        graph_data = self.extract_graph(language, refactorings)
        digraph = self.create_digraph(graph_data)['digraph']
        subgraphs = self.extract_subgraphs(project, digraph, graph_data)['directed_subgraphs']
        groups_subgraph = self.split_supgraphs_atomic_and_overtime(subgraphs)
        
        self.write_json(groups_subgraph.get('atomic'), 'dataset/{}/results'.format(project), 'atomic_subgraphs.json')

        self.write_json(groups_subgraph.get('overtime'), 'dataset/{}/results'.format(project), 'overtime_subgraphs.json')

        return

    def save_graph_to_html(self, project, diggraph, group, id):

        file_name = 'dataset/{}/results/plot/{}_subgraph_{}.html'.format(project, group, id) 
        print('Creating {}'.format(file_name))
        os.makedirs(os.path.dirname(file_name), exist_ok=True)
        with io.open(file_name, 'w', encoding='utf8') as f:
            f.write(diggraph.pipe().decode('utf-8'))
        return

    def plot(self, project, subgraphs, label_group):
        
        for subgraph in subgraphs:
            diggraph = Digraph(format='svg')
            diggraph.attr('node', shape='point', fixedsize='true', width='0.15')
            edges = subgraph.get('edges')
            for edge in edges:
                for refactoring in edge:
                    diggraph.edge(refactoring.get('entityBeforeFullName'), refactoring.get('entityAfterFullName'), color='red', label=refactoring.get('refactoringType'), len='0.1')
            label_text = '\n\nRefactoring subgraph #{}'.format(subgraph.get('id'))
            diggraph.attr(bgcolor='gainsboro', label=label_text, fontcolor='black', rankdir='LR', ratio='auto', pad="0.5,0.5")
            self.save_graph_to_html(project, diggraph, label_group, subgraph.get('id'))    

        return

    def plot_overtime_subgraphs(self, project):
        file_name =  'dataset/{}/results/overtime_subgraphs.json'.format(project)
        with open(file_name) as json_file:
            subgraphs = json.load(json_file)
            self.plot(project, subgraphs, 'overtime')
        pass

    def plot_atomic_subgraphs(self, project):
        file_name =  'dataset/{}/results/atomic_subgraphs.json'.format(project)
        with open(file_name) as json_file:
            subgraphs = json.load(json_file)
            self.plot(project, subgraphs, 'atomic')
        pass

    