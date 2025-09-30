"""
Learning Path Optimization Algorithm
Finds shortest path between concepts considering prerequisites and learning time
"""

import heapq
from typing import List, Dict, Tuple, Set, Optional
from dataclasses import dataclass
from enum import Enum


class NodeType(Enum):
    CONCEPT = "concept"
    PATTERN = "pattern"
    INCIDENT = "incident"
    COMPANY = "company"


@dataclass
class LearningNode:
    """Represents a node in the knowledge graph"""
    id: str
    name: str
    type: NodeType
    learning_hours: float
    difficulty: int
    prerequisites: List[str]
    related_concepts: List[str]


@dataclass
class LearningPath:
    """Represents an optimized learning path"""
    nodes: List[LearningNode]
    total_hours: float
    total_difficulty: int
    prerequisites_satisfied: bool
    path_description: str


class ShortestPathFinder:
    """
    Implements Dijkstra's algorithm modified for learning paths

    Cost function considers:
    - Learning time (hours)
    - Difficulty (1-10 scale)
    - Prerequisite satisfaction
    - Knowledge gaps
    """

    def __init__(self, graph: Dict[str, LearningNode]):
        self.graph = graph
        self.current_knowledge: Set[str] = set()

    def set_current_knowledge(self, concepts: List[str]):
        """Set what the learner already knows"""
        self.current_knowledge = set(concepts)

    def calculate_cost(self, node: LearningNode, path_so_far: List[str]) -> float:
        """
        Calculate cost to learn this node

        Args:
            node: The node to evaluate
            path_so_far: Nodes already in the current path

        Returns:
            Cost score (lower is better)
        """
        # Base cost is learning time
        cost = node.learning_hours

        # Difficulty multiplier (harder concepts cost more)
        difficulty_multiplier = 1.0 + (node.difficulty / 20.0)  # 1.0 to 1.5
        cost *= difficulty_multiplier

        # Prerequisite penalty
        unsatisfied_prereqs = set(node.prerequisites) - self.current_knowledge - set(path_so_far)
        if unsatisfied_prereqs:
            # Heavy penalty for missing prerequisites
            cost += len(unsatisfied_prereqs) * 10.0

        return cost

    def find_shortest_path(
        self,
        start_concept: str,
        end_concept: str,
        max_hours: Optional[float] = None
    ) -> LearningPath:
        """
        Find shortest learning path from start to end concept

        Args:
            start_concept: Starting concept ID
            end_concept: Target concept ID
            max_hours: Optional maximum learning hours

        Returns:
            LearningPath with optimal sequence
        """
        if start_concept not in self.graph or end_concept not in self.graph:
            raise ValueError("Start or end concept not found in graph")

        # Priority queue: (cost, current_node, path, hours, difficulty)
        pq = [(0, start_concept, [start_concept], 0, 0)]
        visited = set()

        while pq:
            cost, current, path, hours, difficulty = heapq.heappop(pq)

            if current in visited:
                continue

            visited.add(current)

            # Check if we reached the goal
            if current == end_concept:
                nodes = [self.graph[node_id] for node_id in path]
                return LearningPath(
                    nodes=nodes,
                    total_hours=hours,
                    total_difficulty=difficulty,
                    prerequisites_satisfied=True,
                    path_description=self._generate_path_description(nodes)
                )

            # Check max hours constraint
            if max_hours and hours > max_hours:
                continue

            # Explore neighbors
            current_node = self.graph[current]

            # Consider prerequisites first
            for prereq_id in current_node.prerequisites:
                if prereq_id in self.graph and prereq_id not in visited:
                    self._explore_neighbor(prereq_id, current, path, hours, difficulty, pq)

            # Then consider related concepts
            for related_id in current_node.related_concepts:
                if related_id in self.graph and related_id not in visited:
                    self._explore_neighbor(related_id, current, path, hours, difficulty, pq)

        # No path found
        return LearningPath(
            nodes=[],
            total_hours=0,
            total_difficulty=0,
            prerequisites_satisfied=False,
            path_description="No valid path found"
        )

    def _explore_neighbor(
        self,
        neighbor_id: str,
        current: str,
        path: List[str],
        hours: float,
        difficulty: int,
        pq: List
    ):
        """Helper to explore a neighboring node"""
        neighbor = self.graph[neighbor_id]
        neighbor_cost = self.calculate_cost(neighbor, path)

        new_path = path + [neighbor_id]
        new_hours = hours + neighbor.learning_hours
        new_difficulty = difficulty + neighbor.difficulty

        heapq.heappush(pq, (
            neighbor_cost,
            neighbor_id,
            new_path,
            new_hours,
            new_difficulty
        ))

    def _generate_path_description(self, nodes: List[LearningNode]) -> str:
        """Generate human-readable path description"""
        if not nodes:
            return "Empty path"

        steps = []
        for i, node in enumerate(nodes, 1):
            steps.append(
                f"{i}. {node.name} ({node.learning_hours}h, difficulty: {node.difficulty}/10)"
            )

        return "\n".join(steps)

    def find_all_prerequisites(self, concept_id: str) -> List[LearningNode]:
        """
        Find all prerequisite concepts in learning order

        Args:
            concept_id: The target concept

        Returns:
            List of prerequisites in learning order
        """
        if concept_id not in self.graph:
            return []

        visited = set()
        result = []

        def dfs(node_id: str):
            if node_id in visited:
                return
            visited.add(node_id)

            node = self.graph[node_id]

            # Visit prerequisites first (depth-first)
            for prereq_id in node.prerequisites:
                if prereq_id in self.graph:
                    dfs(prereq_id)

            result.append(node)

        dfs(concept_id)
        return result[:-1]  # Exclude the target concept itself

    def estimate_mastery_time(
        self,
        target_concepts: List[str],
        hours_per_day: float = 8.0
    ) -> Dict[str, any]:
        """
        Estimate time to master a set of concepts

        Args:
            target_concepts: List of concept IDs to master
            hours_per_day: Available learning hours per day

        Returns:
            Dictionary with time estimates
        """
        all_required = set()

        # Find all prerequisites for each target
        for concept_id in target_concepts:
            prereqs = self.find_all_prerequisites(concept_id)
            all_required.update(node.id for node in prereqs)
            all_required.add(concept_id)

        # Remove already known concepts
        to_learn = all_required - self.current_knowledge

        # Calculate total time
        total_hours = sum(
            self.graph[concept_id].learning_hours
            for concept_id in to_learn
            if concept_id in self.graph
        )

        days = total_hours / hours_per_day
        weeks = days / 7

        return {
            "concepts_to_learn": len(to_learn),
            "total_hours": round(total_hours, 1),
            "days": round(days, 1),
            "weeks": round(weeks, 1),
            "concepts": list(to_learn)
        }

    def identify_knowledge_gaps(
        self,
        target_concept: str
    ) -> Dict[str, List[str]]:
        """
        Identify what's missing to learn target concept

        Args:
            target_concept: The desired concept to learn

        Returns:
            Dictionary categorizing missing knowledge
        """
        if target_concept not in self.graph:
            return {"error": ["Concept not found"]}

        prerequisites = self.find_all_prerequisites(target_concept)
        missing = [p for p in prerequisites if p.id not in self.current_knowledge]

        # Categorize by difficulty
        gaps = {
            "beginner": [],
            "intermediate": [],
            "advanced": [],
            "expert": []
        }

        for prereq in missing:
            if prereq.difficulty <= 3:
                gaps["beginner"].append(prereq.name)
            elif prereq.difficulty <= 6:
                gaps["intermediate"].append(prereq.name)
            elif prereq.difficulty <= 8:
                gaps["advanced"].append(prereq.name)
            else:
                gaps["expert"].append(prereq.name)

        return gaps


def create_learning_plan(
    graph: Dict[str, LearningNode],
    current_knowledge: List[str],
    goals: List[str],
    hours_per_week: float = 40.0,
    max_weeks: int = 16
) -> Dict[str, any]:
    """
    Create comprehensive learning plan

    Args:
        graph: Knowledge graph
        current_knowledge: What learner already knows
        goals: Target concepts to learn
        hours_per_week: Available study hours per week
        max_weeks: Maximum time allowed

    Returns:
        Structured learning plan
    """
    finder = ShortestPathFinder(graph)
    finder.set_current_knowledge(current_knowledge)

    # Estimate time
    estimate = finder.estimate_mastery_time(goals, hours_per_week / 7)

    if estimate["weeks"] > max_weeks:
        return {
            "feasible": False,
            "reason": f"Requires {estimate['weeks']} weeks, only {max_weeks} available",
            "suggestions": [
                "Reduce scope",
                "Increase hours per week",
                "Extend timeline"
            ]
        }

    # Build week-by-week plan
    weekly_plan = []
    hours_budget = hours_per_week
    current_week = []

    # Get all required concepts in order
    all_concepts = set()
    for goal in goals:
        prereqs = finder.find_all_prerequisites(goal)
        all_concepts.update(prereq.id for prereq in prereqs)
        all_concepts.add(goal)

    concepts_to_learn = [
        graph[cid] for cid in all_concepts
        if cid not in current_knowledge and cid in graph
    ]

    # Sort by difficulty and prerequisites
    concepts_to_learn.sort(key=lambda c: (c.difficulty, len(c.prerequisites)))

    week_num = 1
    for concept in concepts_to_learn:
        if hours_budget >= concept.learning_hours:
            current_week.append(concept.name)
            hours_budget -= concept.learning_hours
        else:
            # Start new week
            weekly_plan.append({
                "week": week_num,
                "concepts": current_week,
                "hours_used": hours_per_week - hours_budget
            })
            week_num += 1
            current_week = [concept.name]
            hours_budget = hours_per_week - concept.learning_hours

    # Add last week
    if current_week:
        weekly_plan.append({
            "week": week_num,
            "concepts": current_week,
            "hours_used": hours_per_week - hours_budget
        })

    return {
        "feasible": True,
        "total_concepts": len(concepts_to_learn),
        "total_hours": estimate["total_hours"],
        "total_weeks": len(weekly_plan),
        "weekly_plan": weekly_plan,
        "completion_percentage": round(estimate["weeks"] / max_weeks * 100, 1)
    }


# Example usage
if __name__ == "__main__":
    # Sample graph
    sample_graph = {
        "FUND-001": LearningNode(
            "FUND-001", "Distributed Systems", NodeType.CONCEPT,
            1.0, 1, [], []
        ),
        "FUND-002": LearningNode(
            "FUND-002", "CAP Theorem", NodeType.CONCEPT,
            2.5, 3, ["FUND-001"], ["FUND-003"]
        ),
        "CNSP-005": LearningNode(
            "CNSP-005", "Raft Consensus", NodeType.CONCEPT,
            6.0, 7, ["FUND-002"], []
        ),
    }

    finder = ShortestPathFinder(sample_graph)
    finder.set_current_knowledge(["FUND-001"])

    path = finder.find_shortest_path("FUND-001", "CNSP-005")
    print(f"Path found: {path.total_hours} hours")
    print(path.path_description)

    estimate = finder.estimate_mastery_time(["CNSP-005"])
    print(f"\nMastery estimate: {estimate['weeks']} weeks")