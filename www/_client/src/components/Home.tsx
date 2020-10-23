import React, { Component, useState } from 'react';
import { BenchmarkView } from '../routes/BenchmarkView';
import { IIndexInfo, IConfigurationDto } from '../models/DataModel';
import { Link } from 'react-router-dom';
import { getConfiguration, handleDispatch } from '../init';
import { SimpleLoader } from './SimpleLoader';




export const Home = (props) => {
  // server config
  const [serverConfig, setServerConfig] = useState(getConfiguration());
  const configurations = serverConfig?.benchmarkList;

  // listen for load
  handleDispatch<IConfigurationDto>("configurationLoaded", (data) => {
    setServerConfig(data);
  });

  if (!configurations) {
    return <SimpleLoader />
  }

  return (
    <div className="row">
      {configurations.map((configuration, i) => {

        const newcfg = {
          ...configuration,
          branch: "master"
        };

        return <div key={i} className="chart-wrapper col col-lg-4 col-xl-3 col-md-6 col-sm-12">
          <div className="chart-inner">
            <Link to={`/benchmarks/${i}`}>
              <BenchmarkView
                size="small"
                configuration={newcfg}
                simple
                hideXTicks
                hideBroken={false}
              />
            </Link>
          </div>
        </div>
      })}
    </div>
  );
}
