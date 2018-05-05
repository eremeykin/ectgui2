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
from parameters_dialog.ik_means_dialog import IKMeansParamsDialog
from clustering.agglomerative.utils.choose_p import ChooseP
from parameters_dialog.auto_choose_p import AutoChoosePDialog
import numpy as np

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
        no_params = True
        for key, value in self.parameters.items():
            if value is None:
                continue
            res += "{} = {}; ".format(key, value)
            no_params = False
        if no_params:
            res += "no parameters"
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
        return "BiKM-R"

    @property
    def parameters(self):
        if self._parameters == QDialog.Rejected:
            return None
        epsilon, seed = self._parameters
        return {"epsilon": epsilon, "random seed":seed}

    def ask_parameters(self, parent):
        self._parameters = BiKMeansRParamsDialog.ask(parent)

    def __call__(self, *args, **kwargs):
        start = time()
        epsilon, seed = self._parameters
        rstate = np.random.get_state()
        np.random.seed(seed)
        run_bikm_r = BiKMeansR(self.data, epsilon=epsilon)
        result_labels = run_bikm_r()
        self._time = time() - start
        np.random.set_state(rstate)
        return result_labels, run_bikm_r.cluster_structure


class DEPDDPAlgorithm(AWardAlgorithm):
    def __init__(self, data):
        super(self.__class__, self).__init__(data)

    @property
    def name(self):
        return "dePDDP"

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

    def ask_parameters(self, parent):
        self._parameters = IKMeansParamsDialog.ask(parent)

    @property
    def parameters(self):
        if self._parameters == QDialog.Rejected:
            return None
        threshold = self._parameters
        return {"threshold": threshold}

    def __call__(self, *args, **kwargs):
        threshold = self._parameters
        start = time()
        run_ap_init = APInit(self.data, threshold)
        run_ap_init()
        cs = run_ap_init.cluster_structure
        run_ik_means = IKMeans(cs)
        result_labels = run_ik_means()
        self._time = time() - start
        return result_labels, run_ik_means.cluster_structure


class AutoChoosePAlgorithm(AWardAlgorithm):
    @property
    def name(self):
        return "automatic choosing p beta"

    def ask_parameters(self, parent):
        self._parameters = AutoChoosePDialog.ask(parent)

    @property
    def parameters(self):
        if self._parameters == QDialog.Rejected:
            return None
        start, step, end, clusters_number = self._parameters
        return {"start": start, "step": step, "end": end, "clusters_number": clusters_number}

    def _run_a_ward_pb(self, k_star, p, beta, threshold):
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
        return run_a_ward_pb.cluster_structure

    def __call__(self, *args, **kwargs):
        start, step, end, clusters_number = self._parameters
        threshold = 1
        SW = ChooseP.AvgSilhouetteWidthCriterion()
        sw_list = []
        for p in np.arange(start, end, step):
            for beta in np.arange(start, end, step):
                clusters_structure = self._run_a_ward_pb(clusters_number, p, beta, threshold)
                sw = SW(clusters_structure)
                sw_list.append((sw, p, beta))
                print("p = {}, beta= {}".format(p,beta))
        best = max(sw_list, key=lambda el: el[0])
        return best[1], best[2]
