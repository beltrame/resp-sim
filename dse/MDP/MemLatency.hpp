/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 *   This program is distributed in the hope that it will be useful,       *
 *   but WITHOUT ANY WARRANTY; without even the implied warranty of        *
 *   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the         *
 *   GNU General Public License for more details.                          *
 *                                                                         *
 *   You should have received a copy of the GNU General Public License     *
 *   along with this program; if not, write to the                         *
 *   Free Software Foundation, Inc.,                                       *
 *   59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.             *
 *                                                                         *
 ***************************************************************************/

#ifndef PROCNUM_HPP
#define PROCNUM_HPP

/// This file contains the class representing the parameters number of
/// processors.

#include "pluginIf.hpp"

#ifdef MEMORY_DEBUG
#include <mpatrol.h>
#endif

///This parameter uses as statistic the number of accesses made to memory. Given
///this the only action that can be performed is an increment/decrement
///of the memory latency according to the possible latencies specified at configuration
///time in the configurtion file.
///This means:
///The configuration file has latencies 1,5,10,20
///action increment moves from 1 to 5, from 5 to 10 etc.
///action decrement moves from 10 to 5, 5 to 1 etc.
class MemLatencyIf : public IntegerPlugin{
  public:
    MemLatencyIf(const std::vector<std::string> &values, std::string pluginName);

    ///Given a metric and the new parameter value, we obtain an
    ///estimation of the metric change from the old value to the new
    ///one
    std::pair<float, float> changeValue(plugin_int_map &parameters, int newValue, const std::string &metric,
                            const float_map &centroidMap, const float_map &statistics,
                                                                    const std::map<PluginIf *, std::string> &parameter_values);

    ///It computes the new value of the metrics according to
    ///the specified value and returns it
    void updateStatistics(float_map &curStats, int oldValue, int action, const std::map<PluginIf *, std::string> &parameter_values);

    ///Using the current instance of ReSPClient, it queries ReSP for the new
    ///values of the metrics (i.e. CPI, frequency etc. for a processor) and returns
    ///this value
    void getStats(RespClient &client, float_map &toUpdateStats);

    ///Given the enumeration representing the parameter value of this plugin (i.e. the memory
    ///latency) it returns the corresponding memory latency
    unsigned int getMemoryLatency(int latencyEnum);
};

class MemLatencyCreator : public PluginCreator{
  public:
    MemLatencyCreator();
    ~MemLatencyCreator();
    ///Creates an instance of the plugin; the valid configurations
    ///for the parameter represented by the plugin are passed
    ///to this method
    PluginIf *create(const std::vector<std::string> &values, std::string pluginName);
    ///Destroys an instance of the plugin
    void destroy(PluginIf * toDestroy);
};

#endif
