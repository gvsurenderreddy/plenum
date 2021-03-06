from plenum.server.node import Node

from plenum.common.exceptions import SuspiciousNode
from plenum.server.suspicion_codes import Suspicions
from plenum.test.helper import getPrimaryReplica, getNonPrimaryReplicas, getAllArgs, \
    getNodeSuspicions

nodeCount = 7


def testPrimarySendsAPrepareAndMarkedSuspicious(looper, nodeSet, preprepared1):
    def sendPrepareFromPrimary(instId):
        primary = getPrimaryReplica(nodeSet, instId)
        preprepared1.viewNo = instId
        preprepared1.ppSeqNo = primary.prePrepareSeqNo
        primary.doPrepare(preprepared1)
        for r in getNonPrimaryReplicas(nodeSet, instId):
            l = len([param for param in getAllArgs(r, r.processPrepare)
                     if param['sender'] == primary.name])
            assert l == 1

        sendPrepareFromPrimary(0)

    for node in nodeSet:
        if node in getNonPrimaryReplicas(nodeSet, 0):
            frm, reason, code = getAllArgs(node, Node.reportSuspiciousNode)
            assert frm == getPrimaryReplica(nodeSet, 0).node.name
            assert isinstance(reason, SuspiciousNode)
            assert len(getNodeSuspicions(node, Suspicions.PR_FRM_PRIMARY.code)) \
                   == 10
