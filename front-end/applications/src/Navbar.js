import React, { Component, Fragment } from 'react';
import axios from 'axios';
import { Offcanvas } from 'react-bootstrap'


class Navigator extends Component {
    render() {
        return (
            <nav className="navbar navbar-expand-lg sticky-top navbar-dark bg-dark">

                <div className="container-fluid">
                    <span className="navbar-brand logo">
                        SAC Election Software
                    </span>

                    <div className="collapse navbar-collapse" id="navbarNavAltMarkup">
                        <div className="navbar-nav">
                        </div>
                    </div>
                    <div>
                        <button className="btn btn-outline-light" type="button" id="userTab" onClick={() => this.props.setUserTabShow(true)}>
                            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" className="bi bi-person-circle" viewBox="0 0 16 16">
                                <path d="M11 6a3 3 0 1 1-6 0 3 3 0 0 1 6 0z" />
                                <path fillRule="evenodd" d="M0 8a8 8 0 1 1 16 0A8 8 0 0 1 0 8zm8-7a7 7 0 0 0-5.468 11.37C3.242 11.226 4.805 10 8 10s4.757 1.225 5.468 2.37A7 7 0 0 0 8 1z" />
                            </svg>
                        </button>
                    </div>


                </div>

            </nav>

        );
    }
}

class UserTab extends Component {
    constructor(props) {
        super(props);
        this.state = {
            user: {
                name: '',
                rollNo: '',
                email: '',
                profilePic: '',
            }
        };
    }

    componentDidMount() {
        this.getUserDetails();
    }

    updateState(prop, val) {
        let newState = Object.assign({}, this.state);
        newState[prop] = val;
        this.setState(newState);
    }

    logoutUser() {
        window.location.replace("/auth/logout");
    }

    getUserDetails() {
        axios.get('/auth/get-user', { headers: { 'Accept': 'application/json' } })
            .then((resp) => {
                this.updateState('user', resp.data.user);
            })
            .catch((error) => {
                console.error(error);
            });
    }



    render() {
        return (
            <Offcanvas placement="end" id="userTab" show={this.props.userTabShow} onHide={() => this.props.setUserTabShow(false)}>
                <Offcanvas.Header>
                    <Offcanvas.Title>Logged in as STUDENT</Offcanvas.Title>
                    <button type="button" className="btn-close text-reset" onClick={() => this.props.setUserTabShow(false)}></button>
                </Offcanvas.Header>
                <Offcanvas.Body>
                    <div className="user-tab">
                        <div className="user-pic-div">
                            <img className="user-pic" src={this.state.user.profilePic} />
                        </div>
                        <div>
                            <h2>{this.state.user.name}</h2>
                            <h4>Roll No.: {this.state.user.rollNo}</h4>
                            <h4>Email: {this.state.user.email}</h4>
                        </div>
                        <button className="btn btn-link" onClick={() => this.logoutUser()}>Log Out</button>


                    </div>
                </Offcanvas.Body>

            </Offcanvas>
        );
    }
}

class Navbar extends Component {
    constructor(props) {
        super(props);
        this.state = {
            userTabShow: false
        };
    }

    updateState(prop, val) {
        let newState = Object.assign({}, this.state);
        newState[prop] = val;
        this.setState(newState);
    }

    render() {
        return (
            <Fragment>
                <Navigator setUserTabShow={(val) => this.updateState('userTabShow', val)} />
                <UserTab userTabShow={this.state.userTabShow} setUserTabShow={(val) => this.updateState('userTabShow', val)} />
            </Fragment>
        );
    }
}

export default Navbar;