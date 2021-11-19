import pulumi
from pulumi_azure_native import resources,network,storage,compute

class vmArgs:
    def __init__(self, username: pulumi.Input[str], password: pulumi.Input[str]):
        self.username = username
        self.password = password


class vm(pulumi.ComponentResource):
    def __init__(
        self, name: str, args: vmArgs, opts: pulumi.ResourceOptions = None
    ):
        super().__init__("virtualmachine:index:vm", name, {}, opts)

        # Create an Azure Resource Group
        resource_group = resources.ResourceGroup(name+"resourceGroup")

        network_security_group = network.NetworkSecurityGroup("networkSecurityGroup",
            location=resource_group.location,
            resource_group_name = resource_group.name,
            security_rules=[network.SecurityRuleArgs(
                access="Allow",
                destination_address_prefix="*",
                destination_port_range="22",
                direction="Inbound",
                name="SSH",
                priority=1000,
                protocol="Tcp",
                source_address_prefix="*",
                source_port_range="*"
            )]
        )


        # publicIPAddressResource 
        public_ip_address_res = network.PublicIPAddress("publicIPAddress",
            dns_settings = network.PublicIPAddressDnsSettingsArgs(
                domain_name_label="dnslbl-anirudh",
                ),
            location=resource_group.location,
            resource_group_name = resource_group.name,
            idle_timeout_in_minutes=4,
            public_ip_address_version="IPv4",
            public_ip_allocation_method="Dynamic",
            sku= network.PublicIPAddressSkuArgs(
                name="Basic"
                )
            )

        # virtualNetworkResource
        virtual_network = network.VirtualNetwork("virtualNetwork",
            address_space = network.AddressSpaceArgs(
                address_prefixes=["10.0.0.0/16"],
            ),
            location=resource_group.location,
            resource_group_name = resource_group.name)

        # subnetResource
        subnet = network.Subnet("subnet",
            address_prefix="10.0.0.0/16",
            private_endpoint_network_policies="Enabled",
            private_link_service_network_policies="Enabled",
            resource_group_name=resource_group.name,
            virtual_network_name= virtual_network.name)

        # networkInterfaceResource
        network_interface = network.NetworkInterface("networkInterface",
            ip_configurations=[network.NetworkInterfaceIPConfigurationArgs(
                name="ipconfig1",
                public_ip_address=network.PublicIPAddressArgs(
                    id=public_ip_address_res.id,
                    ),
                subnet=network.SubnetArgs(
                    id=subnet.id,
                    ),
                )],
            location=resource_group.location,
            network_security_group= network.NetworkSecurityGroupArgs(
                id=network_security_group.id
                ),
            resource_group_name=resource_group.name)

        # virtal machine 

        virtual_machine = compute.VirtualMachine("virtualMachine",
            hardware_profile=compute.HardwareProfileArgs(
                vm_size="Standard_D2s_v3",
                ),
            location=resource_group.location,
            network_profile=compute.NetworkProfileArgs(
            network_interfaces=[compute.NetworkInterfaceReferenceArgs(
                id=network_interface.id,
                primary=True,
                )],
            ),
            os_profile=compute.OSProfileArgs(
                admin_username=args.username,
                admin_password=args.password,
                # "admin123" "Unif!12#"
                computer_name="myVM",
                linux_configuration= compute.LinuxConfigurationArgs(
                    patch_settings= compute.LinuxPatchSettingsArgs(
                        assessment_mode="ImageDefault",
                        ),
                    provision_vm_agent=True,
                    ),
                ),
            resource_group_name=resource_group.name,
            storage_profile= compute.StorageProfileArgs(
                image_reference= compute.ImageReferenceArgs(
                    offer="UbuntuServer",
                    publisher="Canonical",
                    sku="16.04-LTS",
                    version="latest",
                    ),
                os_disk= compute.OSDiskArgs(
                    caching="ReadWrite",
                    create_option="FromImage",
                    managed_disk=compute.ManagedDiskParametersArgs(
                        storage_account_type="Premium_LRS",
                        ),
                    name="myVMosdisk",
                    ),
                ),
            )

    




