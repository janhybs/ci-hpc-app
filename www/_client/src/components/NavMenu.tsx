import React from 'react';
// import { Collapse, Container, Navbar, NavbarBrand, NavbarToggler, NavItem, NavLink } from 'reactstrap';
import { Navbar, Container, NavbarBrand, Collapse, NavItem } from 'react-bootstrap';
import { NavLink } from 'react-router-dom';
import './NavMenu.css';


interface NavMenuState {

}

export class NavMenu extends React.Component<NavMenuState, any, any> {
  static displayName = NavMenu.name;

  constructor (props: any) {
    super(props);

    this.toggleNavbar = this.toggleNavbar.bind(this);
    this.state = {
      collapsed: true
    };
  }

  toggleNavbar () {
    this.setState({
      collapsed: !this.state.collapsed
    });
  }

  render () {
    return (
      
      <header>
        <Navbar>
          <Container>
            <NavbarBrand href="/">cc.net</NavbarBrand>
            {/* <NavbarToggler onClick={this.toggleNavbar} className="mr-2" /> */}
            <Collapse in={true}>
              <ul className="navbar-nav flex-grow">
                <NavItem>
                  <NavLink className="text-dark px-2" to="/">Home</NavLink>
                </NavItem>
                <NavItem>
                  <NavLink className="text-dark px-2" to="/scheduler">Scheduler</NavLink>
                </NavItem>
                <NavItem>
                  <NavLink className="text-dark px-2" to="/benchmarks">Benchmarks</NavLink>
                </NavItem>
              </ul>
            </Collapse>
          </Container>
        </Navbar>
      </header>
    );
  }
}