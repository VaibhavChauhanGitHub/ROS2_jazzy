import rclpy
from rclpy.lifecycle import LifecycleNode
from rclpy.lifecycle import State
from rclpy.lifecycle import TransitionCallbackReturn
from conveyor_interfaces.msg import BoxState, SystemAlert
from rclpy.qos import QoSProfile, ReliabilityPolicy


class SafetySupervisorNode(LifecycleNode):
    def __init__(self):
        super().__init__('safety_supervisor_node')
        self.declare_parameter('critical_threshold', 7)
        self.critical_threshold = self.get_parameter('critical_threshold').value
        self.subscription_ = None
        self.alert_publisher_ = None
        self.get_logger().info('Safety Supervisor node has been created.')

    def on_configure(self, state: State):
        self.get_logger().info('Configuring Safety Supervisor node...')
        qos_profile = QoSProfile(
            depth=10,
            reliability=ReliabilityPolicy.RELIABLE
        )
        self.subscription_ = self.create_subscription(
            BoxState,
            '/box_state',
            self.box_state_callback,
            qos_profile
        )
        self.alert_publisher_ = self.create_lifecycle_publisher(
            SystemAlert,
            '/system_alert',
            10
        )
        self.get_logger().info('Safety Supervisor node configured.')
        return TransitionCallbackReturn.SUCCESS

    def on_activate(self, state: State):
        self.get_logger().info('Activating Safety Supervisor node...')
        return super().on_activate(state)

    def on_deactivate(self, state: State):
        self.get_logger().info('Deactivating Safety Supervisor node...')
        return super().on_deactivate(state)

    def on_cleanup(self, state: State):
        self.get_logger().info('Cleaning up Safety Supervisor node...')
        if self.subscription_ is not None:
            self.destroy_subscription(self.subscription_)
            self.subscription_ = None
        if self.alert_publisher_ is not None:
            self.destroy_publisher(self.alert_publisher_)
            self.alert_publisher_ = None
        return TransitionCallbackReturn.SUCCESS

    def box_state_callback(self, msg):
        box_count = msg.box_count
        self.get_logger().info(f'Received box count: {box_count}')
        if box_count > self.critical_threshold:
            alert_msg = SystemAlert()
            alert_msg.level = 'CRITICAL'
            alert_msg.message = (f'Box count {box_count} exceeds 'f'critical threshold of {self.critical_threshold}.')
            self.alert_publisher_.publish(alert_msg)
            self.get_logger().warn(alert_msg.message)

def main(args=None):
    rclpy.init(args=args)
    safety_supervisor_node = SafetySupervisorNode()
    try:
        rclpy.spin(safety_supervisor_node)
    except KeyboardInterrupt:
        pass
    finally:
        safety_supervisor_node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()