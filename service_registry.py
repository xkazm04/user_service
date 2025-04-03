import consul
import socket
import os
import time
import logging
import uuid
import threading

logger = logging.getLogger("service_registry")

class ServiceRegistry:
    def __init__(self):
        self.consul_host = os.getenv("CONSUL_HOST", "consul")
        self.consul_port = int(os.getenv("CONSUL_PORT", "8500"))
        self.service_name = os.getenv("SERVICE_NAME", "user")
        self.service_id = f"{self.service_name}-{uuid.uuid4()}"
        self.service_port = int(os.getenv("SERVICE_PORT", "8002"))
        self.health_check_interval = "10s"
        self.consul_client = consul.Consul(host=self.consul_host, port=self.consul_port)
        self.is_registered = False

    def get_host_ip(self):
        """Get the host IP that's reachable from Consul"""
        try:
            # In Docker networking, we use the service name
            return self.service_name
        except:
            # Fallback to getting the actual hostname
            return socket.gethostname()

    def register_service(self):
        """Register service with Consul"""
        try:
            service_ip = self.get_host_ip()
            
            # Register service
            self.consul_client.agent.service.register(
                name=self.service_name,
                service_id=self.service_id,
                address=service_ip,
                port=self.service_port,
                check={
                    "http": f"http://{service_ip}:{self.service_port}/health",
                    "interval": self.health_check_interval
                }
            )
            
            self.is_registered = True
            logger.info(f"Service {self.service_name} registered with Consul at {service_ip}:{self.service_port}")
            return True
        except Exception as e:
            logger.error(f"Failed to register service with Consul: {str(e)}")
            return False

    def deregister_service(self):
        """Deregister service from Consul"""
        if self.is_registered:
            try:
                self.consul_client.agent.service.deregister(self.service_id)
                self.is_registered = False
                logger.info(f"Service {self.service_name} deregistered from Consul")
                return True
            except Exception as e:
                logger.error(f"Failed to deregister service from Consul: {str(e)}")
                return False
        return True

    def start_heartbeat(self):
        """Start a background thread to maintain service registration"""
        def heartbeat():
            while True:
                if not self.is_registered:
                    self.register_service()
                time.sleep(30)  # Check every 30 seconds
        
        thread = threading.Thread(target=heartbeat, daemon=True)
        thread.start()
        logger.info("Service registry heartbeat started")