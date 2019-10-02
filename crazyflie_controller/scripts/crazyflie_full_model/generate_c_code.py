from acados_template import *
import acados_template as at
from export_ode_model import *
import numpy as np
import scipy.linalg
from ctypes import *
from os.path import dirname, join, abspath

ACADOS_PATH = join(dirname(abspath(__file__)), "../../../acados")

# create render arguments
ra = acados_ocp_nlp()

# export model
model = export_ode_model()

# set model_name
ra.model_name = model.name

Tf = 0.75
N = 50
nx = model.x.size()[0]
nu = model.u.size()[0]
ny = nx + nu
ny_e = nx

# set ocp_nlp_dimensions
nlp_dims     = ra.dims
nlp_dims.nx  = nx
nlp_dims.ny  = ny
nlp_dims.ny_e = ny_e
nlp_dims.nbx = 0
nlp_dims.nbu = nu
nlp_dims.nbx_e = 0
nlp_dims.nu  = model.u.size()[0]
nlp_dims.N   = N

# parameters
g0  = 9.8066    # [m.s^2]
mq  = 33e-3     # [Kg] with one marker
Ct  = 3.25e-4   # [N/Krpm^2]

# bounds
hov_w = np.sqrt((mq*g0)/(4*Ct))
max_thrust = 22

# set weighting matrices
nlp_cost = ra.cost
Q = np.eye(nx)
Q[0,0] = 120.0      # x
Q[1,1] = 100.0      # y
Q[2,2] = 100.0      # z
Q[3,3] = 1.0e-3     # q1
Q[4,4] = 1.0e-3     # q2
Q[5,5] = 1.0e-3     # q3
Q[6,6] = 1.0e-3     # q4
Q[7,7] = 7e-1       # vbx
Q[8,8] = 1.0        # vby
Q[9,9] = 4.0        # vbz
Q[10,10] = 1.0e-5   # wx
Q[11,11] = 1.0e-5   # wy
Q[12,12] = 10.0     # wz

R = np.eye(nu)
R[0,0] = 0.06    # w1
R[1,1] = 0.06    # w2
R[2,2] = 0.06    # w3
R[3,3] = 0.06    # w4

nlp_cost.W = scipy.linalg.block_diag(Q, R)

Vx = np.zeros((ny, nx))
Vx[0,0] = 1.0
Vx[1,1] = 1.0
Vx[2,2] = 1.0
Vx[3,3] = 1.0
Vx[4,4] = 1.0
Vx[5,5] = 1.0
Vx[6,6] = 1.0
Vx[7,7] = 1.0
Vx[8,8] = 1.0
Vx[9,9] = 1.0
Vx[10,10] = 1.0
Vx[11,11] = 1.0
Vx[12,12] = 1.0
nlp_cost.Vx = Vx

Vu = np.zeros((ny, nu))
Vu[13,0] = 1.0
Vu[14,1] = 1.0
Vu[15,2] = 1.0
Vu[16,3] = 1.0
nlp_cost.Vu = Vu

nlp_cost.W_e = 50*Q

Vx_e = np.zeros((ny_e, nx))
Vx_e[0,0] = 1.0
Vx_e[1,1] = 1.0
Vx_e[2,2] = 1.0
Vx_e[3,3] = 1.0
Vx_e[4,4] = 1.0
Vx_e[5,5] = 1.0
Vx_e[6,6] = 1.0
Vx_e[7,7] = 1.0
Vx_e[8,8] = 1.0
Vx_e[9,9] = 1.0
Vx_e[10,10] = 1.0
Vx_e[11,11] = 1.0
Vx_e[12,12] = 1.0

nlp_cost.Vx_e = Vx_e

nlp_cost.yref   = np.array([0, 0, 0.5, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, hov_w, hov_w, hov_w, hov_w])
nlp_cost.yref_e = np.array([0, 0, 0.5, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0])

nlp_con = ra.constraints

nlp_con.lbu = np.array([0,0,0,0])
nlp_con.ubu = np.array([+max_thrust,+max_thrust,+max_thrust,+max_thrust])
nlp_con.x0  = np.array([0,0,0,1,0,0,0,0,0,0,0,0,0])
nlp_con.idxbu = np.array([0, 1, 2, 3])

## set QP solver
#ra.solver_config.qp_solver = 'FULL_CONDENSING_QPOASES'
ra.solver_config.qp_solver = 'PARTIAL_CONDENSING_HPIPM'
ra.solver_config.hessian_approx = 'GAUSS_NEWTON'
ra.solver_config.integrator_type = 'ERK'

# set prediction horizon
ra.solver_config.tf = Tf
ra.solver_config.nlp_solver_type = 'SQP_RTI'
#ra.solver_config.nlp_solver_type = 'SQP'

# set header path
ra.acados_include_path  = f'{ACADOS_PATH}/include'
ra.acados_lib_path      = f'{ACADOS_PATH}/lib'
print(ra.acados_include_path)

acados_solver = generate_solver(model, ra, json_file = 'acados_ocp.json')

print('>> NMPC exported')
