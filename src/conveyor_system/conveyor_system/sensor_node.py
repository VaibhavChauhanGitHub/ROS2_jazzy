import rclpy
from rclpy.node import Node
from conveyor_interfaces.msg import BoxState
from rclpy.qos import QoSProfile, ReliabilityPolicy
import random


class SensorNode(Node):
    def __init__(self):
        super().__init__('sensor_node')
        qos_profile = QoSProfile(
            depth=10,
            reliability=ReliabilityPolicy.RELIABLE
        )
        self.publisher_ = self.create_publisher(
            BoxState,
            '/box_state',
            qos_profile
        )
        self.timer = self.create_timer(1.0,self.publish_box_state)
        self.get_logger().info('Sensor node has been started.')

    def publish_box_state(self):
        box_count = random.randint(0, 10)
        msg = BoxState()
        msg.box_count = box_count
        msg.overload = box_count > 7
        self.publisher_.publish(msg)
        self.get_logger().info(f'Published box count: {box_count}')

def main(args=None):
    rclpy.init(args=args)
    sensor_node = SensorNode()
    try:
        rclpy.spin(sensor_node)
    except KeyboardInterrupt:
        pass

    sensor_node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()