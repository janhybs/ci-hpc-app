import React, { Component } from 'react';
import { Route } from 'react-router';
import { Layout } from './components/Layout';
import { Home } from './components/Home';

import { SchedulerList } from './routes/SchedulerList';
import { BenchmarkView } from './routes/BenchmarkView';


export default class App extends Component {
  static displayName = App.name;

  render () {
    return (
      <Layout>
        <Route exact path='/' component={Home} />
        <Route path='/scheduler' exact={true} component={SchedulerList} />
        <Route path='/benchmarks' exact={true} component={BenchmarkView} />
      </Layout>
    );
  }
}
