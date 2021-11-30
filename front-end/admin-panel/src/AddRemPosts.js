import './App.css';
import { Fragment, Component, createRef } from 'react';
import { ListGroup, Container, InputGroup, FormControl, Button } from 'react-bootstrap'
import axios from 'axios'

class AddRemPosts extends Component {

    constructor(props) {
        super(props);
        this.state = {
            posts: [],
            selectedForRem: []
        };
        this.postNameIP = createRef(null);
    }

    componentDidMount() {
        this.fetchPosts();
    }

    fetchPosts() {
        axios.get("/applications/get-posts", { headers: { 'Accepts': 'application/json' } })
            .then((resp) => {
                let posts = resp.data['posts'];
                let tempSelectedForRem = [];
                posts.forEach(_ => {
                    tempSelectedForRem.push(false);
                });
                this.updateState("posts", posts);
                this.updateState("selectedForRem", tempSelectedForRem);
            })
            .catch((err) => {
                console.error(err);
            })
    }

    addPost() {
        axios.post("/admin/posts/add", { post: this.postNameIP.current.value }, { headers: { 'Accepts': 'application/json' } })
            .then((resp) => {
                if (resp.data.msg && resp.data.msg === "Post already exists") {
                    this.props.setToastAlertMessage("Post already exists.");
                    this.props.setShowToastAlert(true);
                }
                else {
                    this.props.setToastAlertMessage("Post added successfully.");
                    this.props.setShowToastAlert(true);
                    this.fetchPosts();
                }
            })
            .catch((err) => {
                this.props.setToastAlertMessage("Something went wrong.");
                this.props.setShowToastAlert(true);
                console.error(err);
            })
    }


    removePosts() {
        let removedPosts = [];
        this.state.selectedForRem.forEach((val, index) => {
            if (val) {
                removedPosts.push(this.state.posts[index])
            }
        })
        axios.post("/admin/posts/remove", { posts: removedPosts }, { headers: { 'Accepts': 'application/json' } })
            .then(() => {
                this.props.setToastAlertMessage("Posts removed successfully.");
                this.props.setShowToastAlert(true);
                this.fetchPosts();
            })
            .catch((err) => {
                this.props.setToastAlertMessage("Something went wrong.");
                this.props.setShowToastAlert(true);
                console.error(err);
            })
    }

    togglePostForRem(index) {
        let newSelectedForRem = this.state.selectedForRem.slice();
        newSelectedForRem[index] = !newSelectedForRem[index];
        this.updateState("selectedForRem", newSelectedForRem);
    }

    updateState(prop, val) {
        let newState = Object.assign({}, this.state);
        newState[prop] = val;
        this.setState(newState);
    }


    render() {
        let listItems = this.state.posts.map((pos, index) => {
            if (this.state.selectedForRem[index])
                return (
                    <ListGroup.Item action variant="danger" key={index} onClick={() => this.togglePostForRem(index)}>{pos}</ListGroup.Item>
                );
            return (
                <ListGroup.Item action key={index} onClick={() => this.togglePostForRem(index)}>{pos}</ListGroup.Item>
            );
        });
        let buttonActive = this.state.selectedForRem.reduce((res, cur) => (res | cur), false);

        return (
            <Fragment>
                <Container className="add-rem-posts-tab">
                    <InputGroup className="mb-3">
                        <FormControl
                            placeholder="Enter name of the post here" ref={this.postNameIP}
                        />
                        <Button variant="outline-secondary" id="add-post-button" onClick={() => this.addPost()}>
                            Add Post
                        </Button>
                    </InputGroup>
                    <ListGroup>
                        {listItems}
                    </ListGroup>

                    <Button disabled={!buttonActive} variant="danger" id="removeButton" style={{ margin: "10px 0px" }} onClick={() => this.removePosts()}>
                        Remove Selected Posts
                    </Button>
                </Container>
            </Fragment>
        );
    }

}


export default AddRemPosts;
