from starcluster.clustersetup import ClusterSetup
from starcluster.logger import log

class RAID0_Create(ClusterSetup):

        '''
        ### Linux package should be installed mdadm and xfsprogs
        ### For ebs volumes can be created using starcluster and attached to the master instance.
        ### NOTE: device mounted as  /dev/sdz /dev/sdy is known as dev/xvdz and /dev/xvdy respectively
        [plugin raid0_create]
        SETUP_CLASS = raid0_create.RAID0_Create
        raid_devices=2 /dev/xvdz /dev/xvdy
        mount_point=/raid0
        '''

	def __init__(self, raid_devices,mount_point='/raid0'):
		self.raid_devices = raid_devices
		self.mount_point = mount_point
		log.debug('raid_devices  = %s' % self.raid_devices)
		log.debug('mount_point = %s' % self.mount_point)

	def run(self, nodes, master, user, user_shell, volumes):
		log.info('Creating RAID0  using mdadm ')
		mssh = master.ssh
                if mssh.get_status('mdadm -D /dev/md0') != 0:
		   mssh.execute('mdadm --create /dev/md0 --force --run --level=0 --chunk=64 --raid-devices=%s' % self.raid_devices)
		   mssh.execute('mkfs.xfs /dev/md0 ')
                   if mssh.get_status('test -f /etc/lsb-release') == 0 :
                      ## debian or ubuntu
                      mssh.execute('mdadm --detail --scan >> /etc/mdadm/mdadm.conf')
                   if mssh.get_status('test -f /etc/redhat-release') == 0 :
                      ## centos or redhat
                      mssh.execute('mdadm --detail --scan >> /etc/mdadm.conf')
		log.info('Skipping creating RAID0  already exists')
                if not mssh.isdir(self.mount_point):
		   log.info('Creating mount point %s.' % self.mount_point)
		   mssh.execute("mkdir -p {0}".format(self.mount_point))
		mssh.execute("mount -t xfs /dev/md0 {0}".format(self.mount_point))
