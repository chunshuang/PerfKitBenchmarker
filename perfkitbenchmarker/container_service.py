# Copyright 2017 PerfKitBenchmarker Authors. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Contains classes related to managed container services.

For now this just consists of a base cluster class that other container
services will be derived from and a Kubernetes specific variant. This enables
users to run PKB VM based benchmarks on container providers (e.g. Kubernetes)
without pre-provisioning container clusters. In the future, this may be
expanded to support first-class container benchmarks.
"""

from perfkitbenchmarker import events
from perfkitbenchmarker import flags
from perfkitbenchmarker import resource
from perfkitbenchmarker import vm_util

FLAGS = flags.FLAGS

flags.DEFINE_string('kubeconfig', None,
                    'Path to kubeconfig to be used by kubectl. '
                    'If unspecified, it will be set to a file in this run\'s '
                    'temporary directory.')

flags.DEFINE_string('kubectl', 'kubectl',
                    'Path to kubectl tool')

flags.DEFINE_string('container_cluster_cloud', None,
                    'Sets the cloud to use for the container cluster. '
                    'This will override both the value set in the config and '
                    'the value set using the generic "cloud" flag.')

flags.DEFINE_integer('container_cluster_num_vms', None,
                     'Number of nodes in the cluster. Defaults to '
                     'container_cluster.vm_count')


@events.benchmark_start.connect
def _SetKubeConfig(unused_sender, benchmark_spec):
  """Sets the value for the kubeconfig flag if it's unspecified."""
  if not FLAGS.kubeconfig:
    FLAGS.kubeconfig = vm_util.PrependTempDir(
        'kubeconfig' + str(benchmark_spec.sequence_number))
    # Store the value for subsequent run stages.
    benchmark_spec.config.flags['kubeconfig'] = FLAGS.kubeconfig


def GetContainerClusterClass(cloud):
  return resource.GetResourceClass(BaseContainerCluster, CLOUD=cloud)


class BaseContainerCluster(resource.BaseResource):
  """A cluster that can be used to schedule containers."""

  RESOURCE_TYPE = 'BaseContainerCluster'

  def __init__(self, spec):
    super(BaseContainerCluster, self).__init__()
    self.name = 'pkb-%s' % FLAGS.run_uri
    self.machine_type = spec.vm_spec.machine_type
    self.gpu_count = spec.vm_spec.gpu_count
    self.gpu_type = spec.vm_spec.gpu_type
    self.zone = spec.vm_spec.zone
    self.num_nodes = spec.vm_count

  def GetResourceMetadata(self):
    """Returns a dictionary of cluster metadata."""
    metadata = {
        'cloud': self.CLOUD,
        'machine_type': self.machine_type,
        'zone': self.zone,
        'size': self.num_nodes,
    }
    if self.gpu_count:
      metadata.update({
          'gpu_type': self.gpu_type,
          'num_gpus': self.gpu_count,
      })
    return metadata


class KubernetesCluster(BaseContainerCluster):
  """A Kubernetes flavor of Container Cluster."""
  pass
