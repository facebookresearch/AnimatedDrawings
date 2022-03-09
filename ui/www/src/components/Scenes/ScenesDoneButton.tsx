import { Button, Col, Row } from "react-bootstrap";

type Props = {
    isLoading: boolean;
};

const ScenesDoneButton = ({isLoading}: Props) => {
    return (
        <Row className="mt-3 px-1 pb-1">
            <Col xs={12}>
                <Button
                    block
                    disabled={isLoading}
                    size="lg"
                    className="shadow-button"
                >
                    Done
                </Button>
            </Col>
        </Row>
    );
};

export default ScenesDoneButton;
