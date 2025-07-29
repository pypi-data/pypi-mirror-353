Data Models
===========

This section describes the data models used in the Dify client.

App Token
---------

.. py:class:: AppToken

   Represents an API token for an application.

   .. py:attribute:: id: str
      
      Unique identifier for the token

   .. py:attribute:: type: Literal["app"]
      
      Token type, always "app"

   .. py:attribute:: token: str
      
      The actual token string

   .. py:attribute:: last_used_at: Optional[int]
      
      Timestamp of last usage

   .. py:attribute:: created_at: int
      
      Timestamp of creation

Workflow Models
-------------

.. py:class:: WorkflowDraft

   Represents a workflow configuration draft.

   .. py:attribute:: graph: Optional[Graph]
      
      The workflow graph structure

   .. py:attribute:: features: dict
      
      Feature configuration

   .. py:attribute:: environment_variables: list
      
      Environment variables used in the workflow

   .. py:attribute:: conversation_variables: list
      
      Conversation variables used in the workflow

Graph Models
-----------

.. py:class:: Graph

   Represents the complete workflow graph structure.

   .. py:attribute:: nodes: list[GraphNode]
      
      List of nodes in the graph

   .. py:attribute:: edges: list[GraphEdge]
      
      List of edges connecting the nodes

   .. py:attribute:: viewport: Viewport
      
      View configuration for the graph

.. py:class:: GraphNode

   Represents a node in the workflow graph.

   .. py:attribute:: id: str
      
      Unique identifier for the node

   .. py:attribute:: type: str
      
      Node type

   .. py:attribute:: data: dict
      
      Node configuration data

   .. py:attribute:: position: dict
      
      Node position in the graph

   .. py:attribute:: targetPosition: str
      
      Position of target connection point

   .. py:attribute:: sourcePosition: str
      
      Position of source connection point

   .. py:attribute:: positionAbsolute: dict
      
      Absolute position in the graph

   .. py:attribute:: width: int
      
      Node width

   .. py:attribute:: height: int
      
      Node height

.. py:class:: GraphEdge

   Represents an edge connecting two nodes in the workflow graph.

   .. py:attribute:: id: str
      
      Unique identifier for the edge

   .. py:attribute:: type: str
      
      Edge type

   .. py:attribute:: source: str
      
      Source node ID

   .. py:attribute:: sourceHandle: str
      
      Source connection point

   .. py:attribute:: target: str
      
      Target node ID

   .. py:attribute:: targetHandle: str
      
      Target connection point

   .. py:attribute:: data: GraphEdgeData
      
      Edge configuration data

   .. py:attribute:: zIndex: int
      
      Z-index for rendering

.. py:class:: GraphEdgeData

   Configuration data for graph edges.

   .. py:attribute:: sourceType: GraphNodeDataTypes
      
      Type of the source node

   .. py:attribute:: targetType: GraphNodeDataTypes
      
      Type of the target node

   .. py:attribute:: isInIteration: bool
      
      Whether the edge is part of an iteration

.. py:class:: GraphNodeData

   Configuration data for graph nodes.

   .. py:attribute:: type: GraphNodeDataTypes
      
      Node type (start, end, or llm)

   .. py:attribute:: title: str
      
      Node title

   .. py:attribute:: description: str
      
      Node description

   .. py:attribute:: variables: list
      
      List of variables used by the node

.. py:class:: Viewport

   Graph view configuration.

   .. py:attribute:: x: Optional[int]
      
      X coordinate of the viewport (default: 0)

   .. py:attribute:: y: Optional[int]
      
      Y coordinate of the viewport (default: 0)

   .. py:attribute:: zoom: Optional[int]
      
      Zoom level (default: 1) 