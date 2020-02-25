import React from 'react';
// import { Collapse, Container, Navbar, NavbarBrand, NavbarToggler, NavItem, NavLink } from 'reactstrap';
import { Navbar, Container, NavbarBrand, Collapse, NavItem, Nav } from 'react-bootstrap';
import { NavLink } from 'react-router-dom';

import { routes } from "../routes";

export class NavMenu extends React.Component<any, any, any> {
  static displayName = NavMenu.name;

  constructor(props: any) {
    super(props);

    this.toggleNavbar = this.toggleNavbar.bind(this);
    this.state = {
      collapsed: true
    };
  }

  toggleNavbar() {
    this.setState({
      collapsed: !this.state.collapsed
    });
  }


  render() {
    return (

      <header className="mb-2">
        <Navbar expand="sm" variant="dark" bg="dark">
          <Container>
          <NavbarBrand href="/">cc.net</NavbarBrand>
          <Navbar.Toggle aria-controls="basic-navbar-nav" />
            <Navbar.Collapse id="basic-navbar-naav">
              <Nav className="ml-auto">
                {routes.map(i =>
                  <Nav.Link key={i.href} href={i.href}>
                    {i.title}
                  </Nav.Link>
                )}
              </Nav>
            </Navbar.Collapse>
          </Container>
        </Navbar>
      </header>
    );
  }
}
