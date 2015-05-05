/*
* Copyright 2015 Futurewei Inc.
* 
* Licensed under the Apache License, Version 2.0 (the "License");
* you may not use this file except in compliance with the License.
* A copy of the license is included with this distribution. If you did not
* recieve a copy you may obtain a copy of the License at
* 
* http://www.apache.org/licenses/LICENSE-2.0
* 
* Unless required by applicable law or agreed to in writing, software
* distributed under the License is distributed on an "AS IS" BASIS,
* WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
* See the License for the specific language governing permissions and
* limitations under the License.
*/


#include <linux/module.h>
#include <linux/kernel.h>
#include <linux/errno.h>
#include <linux/string.h>
#include <linux/init.h>
#include <linux/interrupt.h>
#include <linux/pci.h>
#include <linux/aer.h>
#include <linux/netdevice.h>
#include <linux/etherdevice.h>
#include <linux/if.h>
#include <linux/if_ether.h>
#include <linux/in.h>
#include <linux/rtnetlink.h>
#include <linux/prefetch.h>
#include <linux/log2.h>

static char *net1 = "eth1";
module_param(net1, charp, 0);
MODULE_PARM_DESC(net1, "The first net device name (default is eth1)");

static char *net2 = "eth2";
module_param(net2, charp, 0);
MODULE_PARM_DESC(net2, "The second net device name (default is eth2)");

static bool print = false;
module_param(print, bool, 0);
MODULE_PARM_DESC(print, "Log forwarding statistics (default is false)");

static int stats_interval = 10000;
module_param(stats_interval, int, 0);
MODULE_PARM_DESC(print, "Forwarding statistics packet interval (default is 10000)");

static bool terminate = false;
module_param(terminate, bool, 0);
MODULE_PARM_DESC(terminate, "Free skb instead of forwarding");

static struct net_device *dev1, *dev2;
int count;

static rx_handler_result_t netdev_frame_hook(struct sk_buff **pskb)
{
        struct sk_buff *skb = *pskb; 
	struct net_device *dev;
            
        if (unlikely(skb->pkt_type == PACKET_LOOPBACK))
                return RX_HANDLER_PASS;
        
	dev = (struct net_device*) rcu_dereference_rtnl(skb->dev->rx_handler_data);
	count++;
	if ( ((count % stats_interval) == 0) && print )
		printk("l2fwd count %d\n", count); 

	if (terminate) {
		kfree_skb(skb);
	} else {
		skb->dev = dev;
		skb_push(skb, ETH_HLEN);
		dev_queue_xmit(skb);
	}
                                           
        return RX_HANDLER_CONSUMED;
}     

static int __init l2fwd_init_module(void)
{
        int err = -1;

	dev1 = dev_get_by_name(&init_net, net1);
        if (!dev1) {
		printk("can't get device %s\n", net1);
                err = -ENODEV;
                goto out;
        }

	dev2 = dev_get_by_name(&init_net, net2);
        if (!dev2) {
		printk("can't get device %s\n", net2);
                err = -ENODEV;
                goto out_dev1;
        }

	rtnl_lock();
        err = netdev_rx_handler_register(dev1, netdev_frame_hook, dev2);
        if (err) {
		printk("can't register rx_handler for device %s\n", net1);
                goto out_dev2;
	}
	dev_set_promiscuity(dev1, 1);

        err = netdev_rx_handler_register(dev2, netdev_frame_hook, dev1);
        if (err) {
		printk("can't register rx_handler for device %s\n", net2);
		netdev_rx_handler_unregister(dev1);
                goto out_dev2;
	}
	dev_set_promiscuity(dev2, 1);

	rtnl_unlock();
	return 0;

out_dev2:
	rtnl_unlock();
	dev_put(dev2);
	dev2 = NULL;
out_dev1:
	dev_put(dev1);
	dev1 = NULL;
out:
	return err;
}

static void __exit l2fwd_exit_module(void)
{
	rtnl_lock();
	if (dev2) {
		dev_put(dev2);
		netdev_rx_handler_unregister(dev1);
	}
	if (dev1) {
		dev_put(dev1);
		netdev_rx_handler_unregister(dev2);
	}
	dev_set_promiscuity(dev1, -1);
	dev_set_promiscuity(dev2, -1);
	rtnl_unlock();
}

module_init(l2fwd_init_module);
module_exit(l2fwd_exit_module);

MODULE_DESCRIPTION("Huawei L2 Forwarding module");
MODULE_LICENSE("Apache");
MODULE_VERSION("0.1");
