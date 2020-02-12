import React, { Component } from 'react';
import { BenchmarkView } from '../routes/BenchmarkView';
import { IIndexInfo } from '../models/DataModel';


const configurations: IIndexInfo[] = [
  {
    project: "flow123d",
    test: "01_square_regular_grid",
    benchmark: "transport.yaml",
    mesh: "1_15662_el",
    cpus: 1
  },
  {
    project: "flow123d",
    test: "01_square_regular_grid",
    benchmark: "transport.yaml",
    mesh: "2_31498_el",
    cpus: 1
  }
];


export class Home extends Component {
  static displayName = Home.name;

  render() {
    return (
      <div>
        {configurations.map((configuration, i) =>
          <span style={{ float: "left" }}>
            <BenchmarkView size="small" key={i} configuration={configuration} simple />
          </span>
        )}
      </div>
    );
  }
}
