from moveit2_commander.core.modules import *
from moveit2_commander.core.service_manager import ServiceManager


class GetPlanningScene_ServiceManager(ServiceManager):
    """
    ServiceManager for the MoveIt2 Get Planning Scene service.
    This class is responsible for managing the service that retrieves the current planning scene
    from the MoveIt2 system.

    Parameters:
    - node (Node): The ROS2 Node instance.
    - *args, **kwargs: Additional arguments for future extensibility.
    """

    def __init__(self, node: Node, *args, **kwargs):
        super().__init__(
            node,
            service_name="/get_planning_scene",
            service_type=GetPlanningScene,
            *args,
            **kwargs,
        )

        self._scene: PlanningScene = None

    @property
    def scene(self) -> PlanningScene:
        """
        Property to get the last retrieved planning scene.

        Returns:
        - PlanningScene: The current planning scene, which includes information about the robot's state,
          the environment, and any obstacles.
        """
        return self._scene

    def run(self) -> PlanningScene:
        """
        Method to retrieve the current planning scene from the MoveIt2 system.

        Returns:
        - PlanningScene: The current planning scene, which includes information about the robot's state,
          the environment, and any obstacles.
        """

        request = GetPlanningScene.Request()
        response: GetPlanningScene.Response = self._send_request(request)

        self._scene = self._handle_response(response)

        return self._scene

    def _handle_response(self, response: GetPlanningScene.Response) -> PlanningScene:
        scene: PlanningScene = response.scene
        return scene
