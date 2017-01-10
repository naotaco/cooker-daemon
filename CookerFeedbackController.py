# coding: UTF-8

import numpy as np

class CookerFeedbackController:
    def __init__(self, target, kp, ki, i_hist_size, i_clamp, kd, d_hist_size, d_clamp, debug_pid_func):
        self.kp = kp
        self.target = target
        self.current = 0.0
        self.i_hist_size = i_hist_size
        self.i_clamp = i_clamp
        self.ki = ki
        self.kd = kd
        self.d_hist_size = d_hist_size
        self.d_clamp = d_clamp
        self.i_history = []
        self.d_history = []
        self.debug_pid_func = debug_pid_func

    def setTarget(self, t):
        self.target = t

    def setCurrentTemperature(self, t):
        self.current = t

        self.i_history.insert(0,t)
        if (len(self.i_history) > self.i_hist_size):
            self.i_history.pop() # remove last item

        self.d_history.insert(0,t)
        if (len(self.d_history) > self.d_hist_size):
            self.d_history.pop() # remove last item


    def integralValue(self):
        s = 0
        for h in self.i_history:
            s += self.target - h

        # clamp
        v = self.ki * s / len(self.i_history)
        v_c = max((-self.i_clamp), min(v, self.i_clamp))
        print("error sum: %f value: %3.2f clamp: %1.2f" % (s, v, v_c))
        return v_c

    def proportionalValue(self):
        return self.kp * (self.target - self.current)

    def derivativeValue(self):
        xdata = []
        ydata = []
        if (len(self.d_history) < 20):
            return 0

        for var in range(0, len(self.d_history)):
            xdata.insert(0, var)
            ydata.insert(len(self.d_history) - 1, self.d_history[var]) # newest value at history[0]

        # print(xdata)
        # print(ydata)

        A = np.array([xdata, np.ones(len(xdata))])
        A = A.T
        a,b = np.linalg.lstsq(A,ydata)[0]

        print("derivative: " + str(a))
        # print("kd: " + str(self.kd))
        # print ("d value: " + str(a * self.kd))
        v = -(a * self.kd)
        v_c = max((-self.d_clamp), min(v, (self.d_clamp)))
        return v_c

    def calcCookerPower(self):
        print ("kp: %2.2f, ki: %2.2f, kd:%2.2f, target: %2.2f, current: %2.2f" % (self.kp, self.ki, self.kd, self.target, self.current))
        p_value = self.proportionalValue()
        i_value = self.integralValue()
        d_value = self.derivativeValue()

        print ("p: %3.3f i: %3.3f d: %3.3f" % (p_value, i_value, d_value))
        self.debug_pid_func(p_value, i_value, d_value)
        return max(0, min((p_value + i_value + d_value), 1.0))
