import React, { Component } from 'react';
import { Route } from 'react-router';
import { Layout } from './components/Layout';

import { routes } from "./routes";


export class App extends Component {
  static displayName = App.name;

  render() {
    return (
      <>
        <Layout>
          {routes.map(i => 
            <Route key={i.href} exact path={i.href} component={i.component} />
          )}
        </Layout>
      </>
    );
  }
}
