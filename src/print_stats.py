# -*- coding: iso-8859-1 -*-
##############################################################################
#
#
#         ___           ___           ___           ___
#        /  /\         /  /\         /  /\         /  /\
#       /  /::\       /  /:/_       /  /:/_       /  /::\
#      /  /:/\:\     /  /:/ /\     /  /:/ /\     /  /:/\:\
#     /  /:/~/:/    /  /:/ /:/_   /  /:/ /::\   /  /:/~/:/
#    /__/:/ /:/___ /__/:/ /:/ /\ /__/:/ /:/\:\ /__/:/ /:/
#    \  \:\/:::::/ \  \:\/:/ /:/ \  \:\/:/~/:/ \  \:\/:/
#     \  \::/~~~~   \  \::/ /:/   \  \::/ /:/   \  \::/
#      \  \:\        \  \:\/:/     \__\/ /:/     \  \:\
#       \  \:\        \  \::/        /__/:/       \  \:\
#        \__\/         \__\/         \__\/         \__\/
#
#
#
#
#   This file is part of ReSP.
#
#   TRAP is free software; you can redistribute it and/or modify
#   it under the terms of the GNU Lesser General Public License as published by
#   the Free Software Foundation; either version 2 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU Lesser General Public License for more details.
#
#   You should have received a copy of the GNU Lesser General Public License
#   along with this program; if not, write to the
#   Free Software Foundation, Inc.,
#   51 Franklin Street, Fifth Floor, Boston, MA  02110-1301  USA
#   or see <http://www.gnu.org/licenses/>.
#
#
#
#   (c) Giovanni Beltrame, Luca Fossati
#       Giovanni.Beltrame@esa.int fossati@elet.polimi.it
#
##############################################################################

import sc_controller_wrapper

class print_stats_cb(sc_controller_wrapper.EOScallback):
    def __call__(self):
        """Prints statistics about the simulation; in case the variable statsPrinter is defined
        in the global namespace (a function must be assigned to it) then that function
        is called passing the globals namespace to it. Otherwise simply the real and simulated
        times are printed; note that before printing statistics, I wait for simulation termination
        (if not otherwise specified)"""
        import time
        while not controller.isEnded():
            time.sleep(0.1)
        try:
            # Call a custom statsprinter if registered
            statsPrinter()
        except NameError:
            # Print
            print 'Real Elapsed Time (seconds):'
            print controller.print_real_time()
            print 'Simulated Elapsed Time (nano-seconds):'
            print str(controller.get_simulated_time()) + '\n'
        except Exception,  e:
            print 'Error in the print of the statistics --> ' + str(e)
