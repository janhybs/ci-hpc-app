import React, { Component } from 'react';
import { BenchmarkView } from '../routes/BenchmarkView';
import { IIndexInfo } from '../models/DataModel';
import { configurations } from '../init';
import { Link } from 'react-router-dom';




export class Home extends Component {
  static displayName = Home.name;

  render() {
    return (
      <div className="row">
        {configurations.map((configuration, i) =>
          <div key={i} className="chart-wrapper col col-lg-4">
            <div className="chart-inner">
              <Link to={`/benchmarks/${i}`}>
                <BenchmarkView
                  size="small" configuration={configuration}
                  simple
                  hideXTicks
                />
              </Link>
            </div>
          </div>
        )}
      </div>
    );
  }
}
