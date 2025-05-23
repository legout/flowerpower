Parent Task: [ROO#TASK_20250523213800_A1B2C3](/.rooroo/tasks/ROO#TASK_20250523213800_A1B2C3/context.md)
Parent Task ID: ROO#TASK_20250523213800_A1B2C3
Previous Sub-Task ID: [ROO#SUB_A1B2C3_S005_20250523234243_E005](/.rooroo/tasks/ROO#SUB_A1B2C3_S005_20250523234243_E005/context.md) (Advanced Pipeline Management)

Goal for Expert (rooroo-developer):
Implement Pipeline Visualization.
1.  Develop UI (htpy + Datastar) to display pipeline Directed Acyclic Graphs (DAGs).
    *   This will likely require a JavaScript library for graph rendering (e.g., Mermaid.js, Cytoscape.js, or similar) that can be integrated with htpy/Datastar. The analyzer from S001 might have suggestions, or the developer may need to research a suitable library.
    *   Nodes in the DAG should be interactive if possible (e.g., display information on hover/click).
2.  Sanic endpoint to fetch pipeline structure data suitable for the chosen visualization library. This might involve using FlowerPower's [`Pipeline.graph`](/src/flowerpower/pipeline/base.py:1) (if it provides a serializable format) or [`PipelineVisualizer`](/src/flowerpower/pipeline/visualizer.py:1).

Key information from parent context:
- User Request (Line [20](/.rooroo/tasks/ROO#TASK_20250523213800_A1B2C3/context.md:20)): Visualize pipeline DAGs with interactive node representations.
- FlowerPower library components for pipeline structure ([`src/flowerpower/pipeline/base.py`](/src/flowerpower/pipeline/base.py:1) - potentially `Pipeline.graph`) and visualization ([`src/flowerpower/pipeline/visualizer.py`](/src/flowerpower/pipeline/visualizer.py:1)).

Dependencies:
- Application with pipeline management features from [ROO#SUB_A1B2C3_S005_20250523234243_E005](/.rooroo/tasks/ROO#SUB_A1B2C3_S005_20250523234243_E005/context.md).
- Analysis report from [ROO#SUB_A1B2C3_S001_20250523233918_A001](/.rooroo/tasks/ROO#SUB_A1B2C3_S001_20250523233918_A001/context.md) might contain suggestions for JS libraries.

Deliverables:
- Updated Sanic application with pipeline DAG visualization.
- Notes on the chosen JS library and how it was integrated.