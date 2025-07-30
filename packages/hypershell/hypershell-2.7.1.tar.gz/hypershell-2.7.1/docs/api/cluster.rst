.. _mod_cluster:

:mod:`hypershell.cluster`
=========================

.. module:: hypershell.cluster
    :platform: Unix, Windows

|

Directly embed the full cluster using one of the available thread variants
(:class:`~hypershell.cluster.local.LocalCluster`, :class:`~hypershell.cluster.remote.RemoteCluster`,
:class:`~hypershell.cluster.remote.AutoScalingCluster`, or :class:`~hypershell.cluster.ssh.SSHCluster`)
or by using one of the provided high-level functions
(:meth:`~hypershell.cluster.local.run_local`, :meth:`~hypershell.cluster.remote.run_cluster`,
or :meth:`~hypershell.cluster.ssh.run_ssh`).

All of the parameters used below are largely the same in each instance. Configuration files have
no impact when using the library; i.e., default values are not overridden by configuration.

.. note::

    The database connection details are only specified via configuration (files or environment).


-------------------

Functions
---------

|

.. autofunction:: hypershell.cluster.local.run_local

|

.. autofunction:: hypershell.cluster.remote.run_cluster

|

.. autofunction:: hypershell.cluster.ssh.run_ssh

-------------------

Classes
-------

|

.. autoclass:: hypershell.cluster.local.LocalCluster
    :show-inheritance:

    .. automethod:: new
    .. automethod:: start
    .. automethod:: join
    .. automethod:: stop

|

.. autoclass:: hypershell.cluster.remote.RemoteCluster
    :show-inheritance:

    .. automethod:: new
    .. automethod:: start
    .. automethod:: join
    .. automethod:: stop

|

.. autoclass:: hypershell.cluster.remote.AutoScalingCluster
    :show-inheritance:

    .. automethod:: new
    .. automethod:: start
    .. automethod:: join
    .. automethod:: stop

|

.. autoclass:: hypershell.cluster.ssh.SSHCluster
    :show-inheritance:

    .. automethod:: new
    .. automethod:: start
    .. automethod:: join
    .. automethod:: stop

-------------------

Constants
---------

|

.. autodata:: hypershell.cluster.remote.DEFAULT_LAUNCHER
.. autodata:: hypershell.cluster.remote.DEFAULT_REMOTE_EXE
.. autodata:: hypershell.cluster.remote.DEFAULT_AUTOSCALE_LAUNCHER
.. autodata:: hypershell.cluster.remote.DEFAULT_AUTOSCALE_POLICY
.. autodata:: hypershell.cluster.remote.DEFAULT_AUTOSCALE_PERIOD
.. autodata:: hypershell.cluster.remote.DEFAULT_AUTOSCALE_FACTOR
.. autodata:: hypershell.cluster.remote.DEFAULT_AUTOSCALE_MIN_SIZE
.. autodata:: hypershell.cluster.remote.DEFAULT_AUTOSCALE_MAX_SIZE
.. autodata:: hypershell.cluster.remote.DEFAULT_AUTOSCALE_INIT_SIZE

|
