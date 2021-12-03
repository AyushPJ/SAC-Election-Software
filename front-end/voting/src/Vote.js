
import './App.css';
import React, { Component, Fragment } from 'react';
import { Container, Nav, Row, Col, Button, Carousel, Table, Toast, ToastContainer } from 'react-bootstrap'
import axios from 'axios'
import Navbar from './Navbar';


class ReviewSubmit extends Component {
  constructor(props) {
    super(props);
    this.submitEnabled = true;
  }

  render() {
    let rows = this.props.selections.map((candidate, index) => {
      let selected = <td className="text-muted">None Selected</td>;
      if (candidate !== null)
        selected = <td>{candidate.name}</td>;
      return (
        <tr key={index}>
          <td>{this.props.posts[index]}</td>
          {selected}
        </tr>
      );
    });

    this.submitEnabled = this.props.selections.every((selection) => {
      return selection != null;
    });
    return (
      <React.Fragment>
        <Row>


          <Table>
            <thead>
              <tr>
                <th style={{ width: "50vh" }}>Post</th>
                <th style={{ width: "50vh" }}>Candidate Name</th>
              </tr>
            </thead>
            <tbody>
              {rows}
            </tbody>
          </Table>


        </Row>
        <Row>
          <Button style={{ width: "50%", margin: "auto" }} variant="success" disabled={!this.submitEnabled} onClick={(e) => this.props.handleSubmit(e)}>Submit</Button>
        </Row>
      </React.Fragment>
    );
  }

}

class Post extends Component {

  render() {
    let caption = "Please select a candidate to view more info and choose as your " + this.props.post + '. You can change your selection afterwards.';
    let dp = null;

    if (this.props.selectedCandidate !== null) {
      dp = <img src={process.env.PUBLIC_URL + "/samplepfp.png"} width="256" height="256"></img>;
      caption = null;
    }
    let candidatesList = this.props.candidates.map((candidate, index) => {
      let active = false;
      if (this.props.selectedCandidate !== null && candidate.applicationNo === this.props.selectedCandidate.applicationNo) {
        active = true;
      }
      return (
        <Nav.Item key={index}>
          <Nav.Link eventKey={index} onClick={(e) => this.props.handleVote(index, candidate, e)} active={active}>
            {candidate.name}
          </Nav.Link>
        </Nav.Item>
      );
    });
    return (
      <Row className="candidates-list">
        <Col xs={6} md={4}>
          <Container>
            <Nav variant="pills" className="flex-column">
              {candidatesList}
            </Nav>
          </Container>
        </Col>
        <Col xs={12} md={8} className="Dp">
          {dp}
          <p>{caption}</p>
        </Col>
      </Row>
    );
  }
}

class Vote extends Component {

  constructor(props) {
    super(props);
    this.state = {
      posts: [],
      selections: [null],
      index: 0,
      candidates: [],
      showToastAlert: false,
    };
    this.toastAlertMessage = "";
  }

  componentDidMount() {
    this.fetchPosts();
    this.fetchCandidates(this.state.index);
  }

  updateState(prop, val) {
    let newState = Object.assign({}, this.state);
    newState[prop] = val;
    this.setState(newState);
  }

  fetchPosts() {
    axios.get("/applications/get-posts", { headers: { 'Accept': 'application/json' } })
      .then((resp) => {
        if (resp.data.posts) {
          let posts = resp.data.posts;
          let selections = posts.map(() => null);
          posts.push("Review & Submit");
          this.updateState("posts", posts);
          this.updateState("selections", selections);
          this.fetchCandidates(posts[0]);
        }
      })
      .catch(function (error) {
        console.log(error);
      });
  }

  fetchCandidates(post, postIndex = null) {
    if (postIndex !== null) {
      post = this.state.posts[postIndex];
    }
    axios.get("/vote/get-candidates/" + post, { headers: { 'Accept': 'application/json' } })
      .then((resp) => {
        let newState = Object.assign({}, this.state);
        if (postIndex !== null)
          newState.index = postIndex;
        newState.candidates = resp.data.candidates;
        newState.candidates.push({ applicationNo: -1, rollNo: -1, name: "None of the above", post: post })
        this.setState(newState);
      })
      .catch(function (error) {
        console.log(error);
      });
  }

  handleSelect(selectedIndex, e) {
    if (selectedIndex !== this.state.posts.length - 1)
      this.fetchCandidates(null, selectedIndex);
    else {
      let newState = Object.assign({}, this.state);
      newState.index = selectedIndex;
      this.setState(newState);
    }

  }

  handleVote(index, candidate, e) {
    let newState = Object.assign({}, this.state);
    newState.selections[newState.index] = { applicationNo: candidate.applicationNo, name: candidate.name, rollNo: candidate.rollNo, post: candidate.post };
    this.setState(newState);
  }

  handleSubmit(e) {
    axios.post("/vote/submit", { votes: this.state.selections }, { headers: { 'Accept': 'application/json' } })
      .then((resp) => {
        this.toastAlertMessage = "Vote saved.";
        this.updateState("showToastAlert", true);
        setTimeout(() => {
          window.location.replace(process.env.REACT_APP_API_SERVER + "/vote/voting-page");
        }, 2000);
      })
      .catch((error) => {
        this.toastAlertMessage = "Something went wrong.";
        this.updateState("showToastAlert", true);
        console.log(error);
      });
    e.preventDefault();
  }

  render() {
    let posts = this.state.posts.map((name, index) => {
      return (
        <Carousel.Item key={index}>
          <img width="500" height="100px" />
          <Carousel.Caption>
            {name}
          </Carousel.Caption>
        </Carousel.Item>
      );
    });

    let display = null;

    if (this.state.index === this.state.posts.length - 1)
      display = <div className="review-submit">
        <ReviewSubmit selections={this.state.selections} posts={this.state.posts} handleSubmit={(e) => this.handleSubmit(e)} />
      </div>;
    else
      display = <div>
        <Post handleVote={(id, name, rollNo, e) => this.handleVote(id, name, rollNo, e)} candidates={this.state.candidates} selectedCandidate={this.state.selections[this.state.index]} post={this.state.posts[this.state.index]} />
      </div>;
    return (
      <Fragment>
        <Navbar />
        <ToastContainer className="p-3 toast-alerts">
          <Toast show={this.state.showToastAlert} onClose={() => this.updateState("showToastAlert", false)} delay={5000} autohide>
            <Toast.Header >
              <strong className="me-auto">{this.toastAlertMessage}</strong>
            </Toast.Header>
          </Toast>
        </ToastContainer>
        <Container>
          <h1>Voting</h1>
        </Container>
        <Container className="container-flex">
          <div className="posts-carousel">
            <Carousel slide={false} interval={null} variant="dark" activeIndex={this.state.index} onSelect={(selectedIndex, e) => this.handleSelect(selectedIndex, e)} >
              {posts}
            </Carousel>
          </div>

          {display}

        </Container>
      </Fragment>
    );
  }
}

export default Vote;
