/*
* Copyright 2015 Futurewei Inc.
*
* l2fwd is free software: you can redistribute it and/or modify
* it under the terms of version 2 the GNU General Public License as published
* by the Free Software Foundation only

* l2fwd is distributed in the hope that it will be useful,
* but WITHOUT ANY WARRANTY; without even the implied warranty of
* MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
* GNU General Public License for more details.

* You should have received a copy of the GNU General Public License
* along with this code.  If not, see
* https://www.gnu.org/licenses/gpl-2.0.html
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
#include <linux/gfp.h>
#include <linux/slab.h>
#include <linux/version.h>

#include <linux/ip.h>
#include <linux/in.h>
#include <linux/icmp.h>
#include <linux/inetdevice.h>


static char *net1 = "eth1";
module_param(net1, charp, 0);
MODULE_PARM_DESC(net1, "The first net device name and optional DNAT parameters (default is eth1)");

static char *net2 = "eth2";
module_param(net2, charp, 0);
MODULE_PARM_DESC(net2, "The second net device name and optional DNAT parameters (default is eth2)");

static bool print = false;
module_param(print, bool, 0);
MODULE_PARM_DESC(print, "Log forwarding statistics (default is false)");

static int stats_interval = 10;
module_param(stats_interval, int, 0);
MODULE_PARM_DESC(print, "Forwarding statistics packet interval (default is 10000)");

static bool terminate = false;
module_param(terminate, bool, 0);
MODULE_PARM_DESC(terminate, "Free skb instead of forwarding");

#if LINUX_VERSION_CODE >= KERNEL_VERSION(3,18,0)
#define BURST_MODE
static short burst = 1;
module_param(burst, short, 0);
MODULE_PARM_DESC(burst, "Send burst-many packets to output device at once (default is 1)");

short burst_count;
#endif
static struct net_device *dev1, *dev2;
int count;

static struct
{
    uint eth1 : 1;
    uint eth2 : 1;
} dnat_enabled;

static uint octet0[4];
static uint mac0[6];
static u8 s_octet0[4];
static u8 s_mac0[6];

static uint octet1[4];
static uint mac1[6];
static u8 s_octet1[4];
static u8 s_mac1[6];
static rx_handler_result_t netdev_frame_hook(struct sk_buff **pskb)
{
    struct sk_buff *skb = *pskb;
    struct net_device *dev;
    char *data = skb->data;
    struct ethhdr *eh = (struct ethhdr *)skb_mac_header(skb);
    struct iphdr *ih = (struct iphdr *)skb_network_header(skb);
    struct icmphdr *icmph = icmp_hdr(skb);

    rx_handler_result_t retval = RX_HANDLER_CONSUMED;

    if (unlikely(skb->pkt_type == PACKET_LOOPBACK))
        return RX_HANDLER_PASS;

    dev = (struct net_device*) rcu_dereference_rtnl(skb->dev->rx_handler_data);
    count++;
    if ( ((count % stats_interval) == 0) && print )
        printk("l2fwd count %d\n", count);

    if (terminate)
        {
            kfree_skb(skb);
        }
    else
        {

            u32 *daddr = &(ih->daddr);
            u32 *saddr = &(ih->saddr);
            unsigned short proto = ntohs(eh->h_proto);

            uint use_dnat = dev == dev1 ? dnat_enabled.eth1:dnat_enabled.eth2;

            if (unlikely(proto != ETH_P_IP ))
                return RX_HANDLER_PASS;

#ifdef DEBUG
            printk("use_dnat %d proto %x ETH_P_IP %x Dest MAC - IP %d.%d.%d.%d MAC %x:%x:%x:%x:%x:%x\n",use_dnat,proto,ETH_P_IP,(u8)daddr[0],(u8)daddr[1],(u8)daddr[2],(u8)daddr[3],eh->h_dest[0],eh->h_dest[1],eh->h_dest[2],eh->h_dest[3],eh->h_dest[4],eh->h_dest[5]);
#endif
            if ( (use_dnat == 1) && (proto == ETH_P_IP) )
                {
                    unsigned int *t_addr = dev == dev1 ? &octet0[0]:&octet1[0];
                    u8 *s_addr = dev == dev1 ? &s_octet0[0]:&s_octet1[0];


                    ((u8 *)daddr)[0] = (u8)t_addr[0];
                    ((u8 *)daddr)[1] = (u8)t_addr[1];
                    ((u8 *)daddr)[2] = (u8)t_addr[2];
                    ((u8 *)daddr)[3] = (u8)t_addr[3];

                    t_addr = dev == dev1 ? &mac0[0]:&mac1[0];

                    eh->h_dest[0] = (unsigned char)t_addr[0];
                    eh->h_dest[1] = (unsigned char)t_addr[1];
                    eh->h_dest[2] = (unsigned char)t_addr[2];
                    eh->h_dest[3] = (unsigned char)t_addr[3];
                    eh->h_dest[4] = (unsigned char)t_addr[4];
                    eh->h_dest[5] = (unsigned char)t_addr[5];

#ifdef DEBUG
                    printk("After DNAT: Dest MAC - IP %d.%d.%d.%d MAC %x:%x:%x:%x:%x:%x\n",daddr[0],daddr[1],daddr[2],daddr[3],eh->h_dest[0],eh->h_dest[1],eh->h_dest[2],eh->h_dest[3],eh->h_dest[4],eh->h_dest[5]);
#endif

                    eh->h_source[0] = (unsigned char)dev->dev_addr[0];
                    eh->h_source[1] = (unsigned char)dev->dev_addr[1];
                    eh->h_source[2] = (unsigned char)dev->dev_addr[2];
                    eh->h_source[3] = (unsigned char)dev->dev_addr[3];
                    eh->h_source[4] = (unsigned char)dev->dev_addr[4];
                    eh->h_source[5] = (unsigned char)dev->dev_addr[5];

                    ((u8 *)saddr)[0] = s_addr[0];
                    ((u8 *)saddr)[1] = s_addr[1];
                    ((u8 *)saddr)[2] = s_addr[2];
                    ((u8 *)saddr)[3] = s_addr[3];

                    skb->ip_summed = CHECKSUM_COMPLETE;
                    skb->csum = skb_checksum_complete(skb);
                    ih->check = 0;
                    ih->check = ip_fast_csum((unsigned char *)ih, ih->ihl);

#ifdef DEBUG
                    printk("After DNAT: Source MAC - IP %d.%d.%d.%d MAC %u:%u:%u:%u:%u:%u\n",saddr[0],saddr[1],saddr[2],saddr[3],eh->h_source[0],eh->h_source[1],eh->h_source[2],eh->h_source[3],eh->h_source[4],eh->h_source[5]);
#endif
                }

            skb->dev = dev;
            skb_push(skb, ETH_HLEN);
#ifdef BURST_MODE
            if (burst > 1)
                {
                   struct netdev_queue *txq = netdev_get_tx_queue(dev, 0);
                   skb_set_queue_mapping(skb, 0);

                   if (!netif_xmit_frozen_or_stopped(txq))
                       {
			   const struct net_device_ops *ops = dev->netdev_ops;
			   int status = NETDEV_TX_OK;
                           skb->xmit_more = --burst_count > 0 ? 1 : 0;
			   status = ops->ndo_start_xmit(skb, dev);
			   if (status == NETDEV_TX_OK)
			       txq_trans_update(txq);
                           if (!burst_count)
                               burst_count = burst;
                       }

                }
	    else
                {
                    dev_queue_xmit(skb);
                }
#else
            dev_queue_xmit(skb);
#endif
        }

    return retval;
}

static int __init l2fwd_init_module(void)
{
    int err = -1;
    char *t_ptr;
    int fCount;
    char *dnat_fmt_suffix = " %3d.%3d.%3d.%3d %2x:%2x:%2x:%2x:%2x:%2x";
    char *dnat_fmt;
    char name_fmt_str[IFNAMSIZ+1];
    char t_name[IFNAMSIZ+1];

#ifdef BURST_MODE
    burst_count = burst;
#endif

    sprintf(name_fmt_str,"%%%ds",IFNAMSIZ);
    dnat_fmt = (char *)kmalloc(strlen(name_fmt_str)+strlen(dnat_fmt_suffix)+1,GFP_KERNEL);
    sprintf(dnat_fmt,"%s%s",name_fmt_str,dnat_fmt_suffix);

    t_ptr=net1;
    while(*t_ptr != '\0') *t_ptr == ',' ? *t_ptr++ = ' ':*t_ptr++;

    fCount = sscanf(net1,dnat_fmt,t_name,&octet0[0],&octet0[1],&octet0[2],
                                         &octet0[3],&mac0[0],&mac0[1],
                                         &mac0[2],&mac0[3],&mac0[4],&mac0[5]);

    dev1 = dev_get_by_name(&init_net, t_name);
    if (!dev1)
        {
            printk("can't get device %s\n", t_name);
            err = -ENODEV;
            goto out;
        }
    if (fCount >1 && fCount <11 )
        {
            printk("Both DNAT IP and Mac Address must be provided\n");
            err = -EINVAL;
            goto out;
        }
    else if (fCount==11 )
        {
            struct in_device *in_dev = rcu_dereference(dev1->ip_ptr);
            __be32 ifaddr = 0;
            struct in_ifaddr *ifap;

            dnat_enabled.eth1 = 1;
            // in_dev has a list of IP addresses (because an interface can have multiple)
            for (ifap = in_dev->ifa_list; ifap != NULL;
                    ifap = ifap->ifa_next)
                {
                    ifaddr = ifap->ifa_address; // is the IPv4 address
                }
            if (ifaddr == 0)
                {
                    printk("%s interface ip address list is null!\n",t_name);
                    err = -ENODEV;
                    goto out;
                }

            s_octet0[0] = ((u8 *)&ifaddr)[0];
            s_octet0[1] = ((u8 *)&ifaddr)[1];
            s_octet0[2] = ((u8 *)&ifaddr)[2];
            s_octet0[3] = ((u8 *)&ifaddr)[3];

            s_mac0[0] = dev1->dev_addr[0];
            s_mac0[1] = dev1->dev_addr[1];
            s_mac0[2] = dev1->dev_addr[2];
            s_mac0[3] = dev1->dev_addr[3];
            s_mac0[4] = dev1->dev_addr[4];
            s_mac0[5] = dev1->dev_addr[5];

#ifdef DEBUG
            printk("DNAT Enabled for %s IP %d.%d.%d.%d MAC %x:%x:%x:%x:%x:%x\n",t_name,octet0[0],octet0[1],octet0[2],octet0[3],mac0[0],mac0[1],mac0[2],mac0[3],mac0[4],mac0[5]);
            printk("SNAT IP %d.%d.%d.%d SNAT MAC  %x:%x:%x:%x:%x:%x\n",s_octet0[0],s_octet0[1],s_octet0[2],s_octet0[3],s_mac0[0],s_mac0[1],s_mac0[2],s_mac0[3],s_mac0[4],mac0[5]);
        }
    else if (fCount==1 )
        {
            printk("Pure Level 2 forward enabled for %s\n",t_name);
#endif
        }


    t_ptr=net2;
    while(*t_ptr != '\0') *t_ptr == ',' ? *t_ptr++ = ' ':*t_ptr++;

    fCount = sscanf(net2,dnat_fmt,t_name,&octet1[0],&octet1[1],&octet1[2],&octet1[3],&mac1[0],&mac1[1],&mac1[2],&mac1[3],&mac1[4],&mac1[5]);

    dev2 = dev_get_by_name(&init_net, t_name);
    if (!dev2)
        {
            printk("can't get device %s\n", t_name);
            err = -ENODEV;
            goto out_dev1;
        }
    if (fCount >1 && fCount <11 )
        {
            printk("Both DNAT IP and Mac Address must be provided\n");
            err = -EINVAL;
            goto out;
        }
    else if (fCount==11 )
        {
            struct in_device *in_dev = rcu_dereference(dev2->ip_ptr);
            __be32 ifaddr = 0;
            struct in_ifaddr *ifap;
            // dev has a list of IP addresses (because an interface can have multiple)
            dnat_enabled.eth2 = 1;
            for (ifap = in_dev->ifa_list; ifap != NULL;
                    ifap = ifap->ifa_next)
                {
                    ifaddr = ifap->ifa_address; // is the IPv4 address
                }
            if (ifaddr == 0)
                {
                    printk("%s interface ip address list is null!\n",t_name);
                    err = -ENODEV;
                    goto out;
                }
            /* ifa_local: ifa_address is the remote point in ppp */

            s_octet1[0] = ((u8 *)&ifaddr)[0];
            s_octet1[1] = ((u8 *)&ifaddr)[1];
            s_octet1[2] = ((u8 *)&ifaddr)[2];
            s_octet1[3] = ((u8 *)&ifaddr)[3];

            s_mac1[0] = dev2->dev_addr[0];
            s_mac1[1] = dev2->dev_addr[1];
            s_mac1[2] = dev2->dev_addr[2];
            s_mac1[3] = dev2->dev_addr[3];
            s_mac1[4] = dev2->dev_addr[4];
            s_mac1[5] = dev2->dev_addr[5];

#ifdef NEVER
            printk("DNAT Enabled for %s IP %d.%d.%d.%d MAC %x:%x:%x:%x:%x:%x\n",t_name,octet1[0],octet1[1],octet1[2],octet1[3],mac1[0],mac1[1],mac1[2],mac1[3],mac1[4],mac1[5]);
            printk("SNAT IP %d.%d.%d.%d SNAT MAC  %x:%x:%x:%x:%x:%x\n",s_octet1[0],s_octet1[1],s_octet1[2],s_octet1[3],s_mac1[0],s_mac1[1],s_mac1[2],s_mac1[3],s_mac1[4],mac1[5]);
        }
    else if (fCount==1 )
        {
            printk("Level 2 forward enabled for %s\n",t_name);
#endif
        }

    rtnl_lock();
    err = netdev_rx_handler_register(dev1, netdev_frame_hook, dev2);
    if (err)
        {
            printk("can't register rx_handler for device %s\n", net1);
            goto out_dev2;
        }
    dev_set_promiscuity(dev1, 1);

    err = netdev_rx_handler_register(dev2, netdev_frame_hook, dev1);
    if (err)
        {
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
    if (dev2)
        {
            dev_put(dev2);
            netdev_rx_handler_unregister(dev1);
        }
    if (dev1)
        {
            dev_put(dev1);
            netdev_rx_handler_unregister(dev2);
        }
    dev_set_promiscuity(dev1, -1);
    dev_set_promiscuity(dev2, -1);
    rtnl_unlock();
}

module_init(l2fwd_init_module);
module_exit(l2fwd_exit_module);

MODULE_DESCRIPTION("Huawei L2 Forwarding module with DNAT");
MODULE_LICENSE("GPL");
MODULE_VERSION("1.0");
