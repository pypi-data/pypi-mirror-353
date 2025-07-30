""" 
Tests for eigenvalue analyses
"""
import unittest
import numpy as np    
import os
from welib.system.mbc import *

MyDir=os.path.dirname(__file__)

class Test(unittest.TestCase):

    def test_mbc3_rot2fixed(self):
        # Test that a simple sine expansion in the rot frame leads to constant MBC coeffs
        #   qrot = C + A*np.cos(om t+psi)   +  B*sin(om t +psi)
        #    >>> a0=C, b0=A, b1 = B

        Omega = 0.1
        psi0_1 = 0
        psi0_2 = psi0_1 + (2 * np.pi / 3)
        psi0_3 = psi0_2 + (2 * np.pi / 3)
        nqb=1; nf=0
        n= nqb*3+nf

        # --- From rotating to fixed
        time = np.array([0,1]) #np.linspace(0,100,100)
        xrot = np.zeros((len(time), n))
        xrot[:,0]=5+2*np.sin(Omega*time + psi0_1)+3*np.cos(Omega*time + psi0_1)
        xrot[:,1]=5+2*np.sin(Omega*time + psi0_2)+3*np.cos(Omega*time + psi0_2)
        xrot[:,2]=5+2*np.sin(Omega*time + psi0_3)+3*np.cos(Omega*time + psi0_3)

        z = MBC3_Rot2Fixed_TS(Omega, time, xrot, nqb=1, nf=0)

        np.testing.assert_array_almost_equal(z[:,0], 5*np.ones(time.shape)) # a0
        np.testing.assert_array_almost_equal(z[:,1], 3*np.ones(time.shape)) # a1
        np.testing.assert_array_almost_equal(z[:,2], 2*np.ones(time.shape)) # b1

    def test_mbc3_fixed2rot(self):
        # Test that cos / sine are returned with a1 or b1 is constant
        Omega = 0.1
        psi0_1 = 0
        nqb=1; nf=0
        n= nqb*3+nf

        # --- From rotating to fixed - Cos component only
        time = np.linspace(0,2*np.pi/Omega,20)
        xf = np.zeros((len(time), n))
        xf[:,0]=0
        xf[:,1]=1
        xf[:,2]=0
        xrot = MBC3_Fixed2Rot_TS(Omega, time, xf, nqb=1, nf=0)
        np.testing.assert_array_almost_equal(xrot[:,0], np.cos(Omega*time))
        np.testing.assert_array_almost_equal(xrot[:,1], np.cos(Omega*time+2*np.pi/3))
        np.testing.assert_array_almost_equal(xrot[:,2], np.cos(Omega*time+4*np.pi/3))
        # --- From rotating to fixed - sine component only
        xf[:,0]=0
        xf[:,1]=0
        xf[:,2]=1
        xrot = MBC3_Fixed2Rot_TS(Omega, time, xf, nqb=1, nf=0)
        np.testing.assert_array_almost_equal(xrot[:,0], np.sin(Omega*time))
        np.testing.assert_array_almost_equal(xrot[:,1], np.sin(Omega*time+2*np.pi/3))
        np.testing.assert_array_almost_equal(xrot[:,2], np.sin(Omega*time+4*np.pi/3))
        # --- From rotating to fixed - cst component only
        xf[:,0]=2
        xf[:,1]=0
        xf[:,2]=0
        xrot = MBC3_Fixed2Rot_TS(Omega, time, xf, nqb=1, nf=0)
        np.testing.assert_array_almost_equal(xrot[:,0], 2+time*0)
        np.testing.assert_array_almost_equal(xrot[:,1], 2+time*0)
        np.testing.assert_array_almost_equal(xrot[:,2], 2+time*0)


    def test_mbc3_mat(self):
        # Test matrices B, Bdot, Bddot, and Binv computed analytically or numerically
        # --- One DOF per blade, no shaft dof
        Omega = 0.1
        B, Binv, Bdot, Bddot, mu, R = MBC3_Bmat(nqb=1, nf=2, psi1=np.pi/12, Omega=Omega)
        Binv_num= np.linalg.inv(B)
        R_num = Binv.dot(Bdot)
        np.testing.assert_array_almost_equal(Binv, Binv_num, 8)
        np.testing.assert_array_almost_equal(R, R_num, 8)
        np.testing.assert_array_almost_equal(Bdot, B @ R, 8)
        np.testing.assert_array_almost_equal(Bddot, B @ R @ R, 8)

        # Compute B at t+dt, check that Bdot using finite differences
        dt=0.001
        B1 = MBC3_Bmat(nqb=1, nf=2, psi1=np.pi/12+Omega*dt, Omega=Omega)[0]
        Bdot_num = (B1-B)/dt
        np.testing.assert_array_almost_equal(Bdot, Bdot_num, 5)

        # --- One DOF per blade with shaft DOFs
        Omega = 0.1
        t=0.4
        B, Binv, Bdot, Bddot, mu, R = MBC3_Bmat(nqb=1, nf=2, psi1=np.pi/12, psi0=Omega*t, Omega=Omega, ns=2)
        Binv_num= np.linalg.inv(B)
        R_num = Binv.dot(Bdot)
        np.testing.assert_array_almost_equal(Binv, Binv_num, 8)
        np.testing.assert_array_almost_equal(R, R_num, 8)
        np.testing.assert_array_almost_equal(Bdot, B @ R, 8)
        np.testing.assert_array_almost_equal(Bddot, B @ R @ R, 8)

    def test_mbc3_mat_sympy(self):
        import sympy as sp
        from sympy import diff
        from sympy.physics.mechanics import dynamicsymbols
        # Test matrices B, Bdot and Binv computed using sympy and numpy
        # --- One DOF per blade, no shaft DOF
        ordering='increasing'
        # Symbolic calculation
        Omega, psi1, psi2, psi3 = dynamicsymbols('Omega, psi_1, psi_2, psi_3')
        time = dynamicsymbols._t
        B, Binv, Bdot, Bddot, mu, R = MBC3_Bmat(1, 2, psi1, Omega=Omega, ordering=ordering, symb=True)
        # Numerical
        Omega_num = 0.1
        psi1_num = np.pi/12
        B_num, Binv_num, Bdot_num, Bddot_num, mu_num, R_num = MBC3_Bmat(1, 2, psi1=psi1_num, Omega=Omega_num, ordering=ordering, symb=False)
        # Comparison
        numSubs=[(psi1, psi1_num), (Omega, Omega_num)]
        np.testing.assert_almost_equal(sp.N(B.subs(numSubs))   ,B_num    )
        np.testing.assert_almost_equal(sp.N(Binv.subs(numSubs)),Binv_num )
        np.testing.assert_almost_equal(sp.N(mu.subs(numSubs))  ,mu_num   )
        np.testing.assert_almost_equal(sp.N(Bdot.subs(numSubs)),Bdot_num )
        np.testing.assert_almost_equal(sp.N(R.subs(numSubs))   ,R_num )

        # --- shaft DOF, verify derivative of B analytically
        B, Binv, Bdot, Bddot, mu, R = MBC3_Bmat(1, 2, psi1, psi2, psi3, psi0=Omega*time, Omega=Omega, ordering=ordering, symb=True, ns=2)
        Subs = [(diff(psi1, time), Omega),(diff(psi2, time), Omega),(diff(psi3, time), Omega),(diff(Omega,time),0)]
        Bdot_sp = diff(B,time).subs(Subs)
        DBdot = (Bdot_sp-Bdot)
        DBdot.simplify()
        np.testing.assert_almost_equal(sp.N(DBdot), np.zeros((7,7) ))
        Bddot_sp = diff(Bdot,time).subs(Subs)
        DBddot = (Bddot_sp-Bddot)
        DBddot.simplify()
        np.testing.assert_almost_equal(sp.N(DBddot), np.zeros((7,7) ))



    def test_mbc3_misc(self):
        # --- One blade
        Omega = 0.1
        # Phase offsets
        psi0_1 = 0
        psi0_2 = psi0_1 + (2 * np.pi / 3)
        psi0_3 = psi0_2 + (2 * np.pi / 3)

        B = MBC3_Bmat(nqb=1, nf=0, psi1=0, Omega=Omega)[0]

        Binv= np.linalg.inv(B)

        M = np.array([
            [1/3,1/3,1/3],
            [2/3*np.cos(psi0_1),2/3*np.cos(psi0_2),2/3*np.cos(psi0_3)],
            [2/3*np.sin(psi0_1),2/3*np.sin(psi0_2),2/3*np.sin(psi0_3)],
            ])
        Minv = np.linalg.inv(M)
#         print('B^{-1}')
#         print(Binv)
#         print('M')
#         print(M)
#         print('B')
#         print(B)
#         print('M^{-1}')
#         print(Minv)
        import matplotlib.pyplot as plt

        time=np.linspace(0,100,100)


        # --- From rotating to fixed
        xrot = np.zeros((len(time),3))
#         xrot[:,0] = np.ones(time.shape)*3
#         xrot[:,1] = np.ones(time.shape)*1.5
#         xrot[:,2] = np.ones(time.shape)*-0.9
#         xrot[:,0]=5+2*np.sin(Omega*time + psi0_1)+3*np.cos(Omega*time + psi0_1)
#         xrot[:,1]=5+2*np.sin(Omega*time + psi0_2)+3*np.cos(Omega*time + psi0_2)
#         xrot[:,2]=5+2*np.sin(Omega*time + psi0_3)+3*np.cos(Omega*time + psi0_3)
#         xrot[:,0]=3*np.cos(Omega*time + psi0_1)
#         xrot[:,1]=3*np.cos(Omega*time + psi0_2)
#         xrot[:,2]=3*np.cos(Omega*time + psi0_3)
#         xf = MBC3_Rot2Fixed_TS(Omega, time, xrot, nqb=1, nf=0)

#         # --- From fixed to rotating
        # NOTE: sum of a1*cos(omt+phi) + b1*sin(omt+phi) = sqrt(xxx)*cos(omt+ yyy)
        xf   = np.zeros((len(time),3))
        #xf[:,0]=5+2*np.sin(Omega*time + psi0_1)+3*np.cos(Omega*time + psi0_1)
        #xf[:,1]=5+2*np.sin(Omega*time + psi0_2)+3*np.cos(Omega*time + psi0_2)
        #xf[:,2]=5+2*np.sin(Omega*time + psi0_3)+3*np.cos(Omega*time + psi0_3)

        #xf[:,0]=14*np.sin(Omega*time + psi0_1)**2 + 12
        #xf[:,1]=0
        #xf[:,2]=0
        # Henriksen example
#         xf[:,0] = 3
#         xf[:,1] = 1.5
#         xf[:,2] = -0.9
        xf[:,0]=0
        xf[:,1]=0
        xf[:,2]=1
        xrot = MBC3_Fixed2Rot_TS(Omega, time, xf, nqb=1, nf=0)

        # Plot
        fig,axes = plt.subplots(2, 1, sharey=False, figsize=(6.4,4.8)) # (6.4,4.8)
        fig.subplots_adjust(left=0.12, right=0.95, top=0.95, bottom=0.11, hspace=0.20, wspace=0.20)
        ax=axes[0]
        ax.plot(time,xf[:,0],'-'     , label='a_0 (coll)')
        ax.plot(time,xf[:,1],':'     , label='a_1 (cos) ')
        ax.plot(time,xf[:,2],'--'    , label='b_1 (sine)')
        ax.legend()
        ax.set_title('Fixed frame coordinates')
        ax=axes[1]
        ax.plot(time,xrot[:,0],'-'    , label='q1 rot B1')
        ax.plot(time,xrot[:,1],':'    , label='q2 rot B2')
        ax.plot(time,xrot[:,2],'--'   , label='q3 rot B3')
        ax.set_title('Rotating frame')
        ax.set_xlabel('')
        ax.set_ylabel('')
        ax.legend()
#         plt.show()
        #np.testing.assert_almost_equal(e[0], -2.44985, 4)


if __name__ == '__main__':
    #np.set_printoptions(linewidth=300, precision=3)
    #Test().test_mbc3_mat()
    unittest.main()
