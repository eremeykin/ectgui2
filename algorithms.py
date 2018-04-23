from time import time
from clustering.agglomerative.pattern_initialization.ap_init import APInit
from clustering.agglomerative.ik_means.ik_means import IKMeans
from clustering.agglomerative.a_ward import AWard
from parameters_dialog.a_ward_dialog import *
from parameters_dialog.a_ward_dialog_pb import *
from parameters_dialog.bikm_r_dialog import *
from clustering.agglomerative.pattern_initialization.ap_init_pb import APInitPB
from clustering.agglomerative.utils.imwk_means_cluster_structure import IMWKMeansClusterStructure
from clustering.agglomerative.ik_means.ik_means import IKMeans
from clustering.agglomerative.a_ward_pb import AWardPB
from clustering.divisive.bikm_r import BiKMeansR
from clustering.divisive.depddp import DEPDDP

from clustering.agglomerative.pattern_initialization.ap_init import APInit
from clustering.agglomerative.ik_means.ik_means import IKMeans
from clustering.agglomerative.a_ward import AWard


class AWardAlgorithm:
    def __init__(self, data):
        self.data = data
        self._parameters = None
        self._time = None

    @classmethod
    def create(cls, data):
        return cls(data)

    @property
    def time(self):
        return self._time

    @property
    def name(self):
        return "A-Ward"

    @property
    def parameters(self):
        if self._parameters == QDialog.Rejected:
            return None
        k_star, alpha, threshold = self._parameters
        return {"K*": k_star, "merge threshold": alpha, "threshold": threshold}

    def ask_parameters(self, parent):
        self._parameters = AWardParamsDialog.ask(parent)

    def __call__(self, *args, **kwargs):
        start = time()
        k_star, alpha, threshold = self._parameters
        run_ap_init = APInit(self.data, threshold)
        run_ap_init()
        run_ik_means = IKMeans(run_ap_init.cluster_structure)
        run_ik_means()
        cs = run_ik_means.cluster_structure
        run_a_ward = AWard(cs, k_star, alpha)
        result_labels = run_a_ward()
        self._time = time() - start
        return result_labels, run_a_ward.cluster_structure

    def __str__(self):
        res = "{} with ".format(self.name)
        for key, value in self.parameters.items():
            if value is None:
                continue
            res += "{} = {}; ".format(key, value)
        return res


class AWarbPBAlgorithm(AWardAlgorithm):
    def __init__(self, data):
        super(self.__class__, self).__init__(data)

    @property
    def name(self):
        return "A-Ward_p_beta"

    @property
    def parameters(self):
        if self._parameters == QDialog.Rejected:
            return None
        k_star, p, beta, threshold = self._parameters
        return {"K*": k_star, "p": p, "beta": beta, "threshold": threshold}

    def ask_parameters(self, parent):
        self._parameters = AWardPBParamsDialog.ask(parent)

    def __call__(self, *args, **kwargs):
        start = time()
        k_star, p, beta, threshold = self._parameters
        run_ap_init_pb = APInitPB(self.data, p, beta, threshold)
        run_ap_init_pb()
        # change cluster structure to matlab compatible
        clusters = run_ap_init_pb.cluster_structure.clusters
        new_cluster_structure = IMWKMeansClusterStructure(self.data, p, beta)
        new_cluster_structure.add_all_clusters(clusters)
        run_ik_means = IKMeans(new_cluster_structure)
        run_ik_means()
        cs = run_ik_means.cluster_structure
        run_a_ward_pb = AWardPB(cs, k_star)
        result_labels = run_a_ward_pb()
        self._time = time() - start
        return result_labels, run_a_ward_pb.cluster_structure


class BiKMeansRAlgorithm(AWardAlgorithm):
    def __init__(self, data):
        super(self.__class__, self).__init__(data)

    @property
    def name(self):
        return "Bi K-Means R"

    @property
    def parameters(self):
        if self._parameters == QDialog.Rejected:
            return None
        epsilon = self._parameters
        return {"epsilon": epsilon}

    def ask_parameters(self, parent):
        self._parameters = BiKMeansRParamsDialog.ask(parent)

    def __call__(self, *args, **kwargs):
        start = time()
        epsilon = self._parameters
        run_bikm_r = BiKMeansR(self.data, epsilon=epsilon)
        result_labels = run_bikm_r()
        self._time = time() - start
        return result_labels, run_bikm_r.cluster_structure


class DEPDDPAlgorithm(AWardAlgorithm):
    def __init__(self, data):
        super(self.__class__, self).__init__(data)

    @property
    def name(self):
        return "de PDDP"

    @property
    def parameters(self):
        if self._parameters == QDialog.Rejected:
            return None
        return dict()

    def ask_parameters(self, parent):
        self._parameters = True

    def __call__(self, *args, **kwargs):
        start = time()
        run_depddp = DEPDDP(self.data)
        result_labels = run_depddp()
        self._time = time() - start
        return result_labels, run_depddp.cluster_structure


class IKMeansAlgorithm(AWardAlgorithm):
    def __init__(self, data):
        super(self.__class__, self).__init__(data)

    @property
    def name(self):
        return "iK-Means"

    def __call__(self, *args, **kwargs):
        k_star, alpha, threshold = self._parameters
        start = time()
        run_ap_init = APInit(self.data, threshold)
        run_ap_init()
        cs = run_ap_init.cluster_structure
        run_a_ward = AWard(cs, k_star, alpha)
        run_a_ward()
        run_ik_means = IKMeans(run_ap_init.cluster_structure)
        result_labels = run_ik_means()
        self._time = time() - start
        return result_labels, run_ik_means.cluster_structure
