import { useEffect, useState } from "react";
import { Button, Col, Row } from "react-bootstrap";
import { useDrawingApi } from "../../hooks/useDrawingApi";
import useDrawingStore from "../../hooks/useDrawingStore";

type Props = {
    isLoading: boolean;
    webPUrl: string | undefined;
};

type AnimatedDrawingObj = {
    videoUrl: string;
    base64Preview: string;
    title: string;
};

declare global {
    interface Window {
        webkit?: {
            messageHandlers?: {
                animatedDrawingMessageHandler?: {
                    postMessage: (obj: AnimatedDrawingObj) => void;
                }
            }
        }
    }
}

const ScenesDoneButton = ({ isLoading, webPUrl }: Props) => {
    const { animationType, uuid } = useDrawingStore();
    const [base64Preview, setBase64Preview] = useState<string>();
    const { getCroppedImage } = useDrawingApi((err) => { });

    const onDoneClicked = () => {
        if (!webPUrl || !base64Preview) {
            return;
        }

        const handler = window.webkit?.messageHandlers?.animatedDrawingMessageHandler;
        if (!handler) {
            return;
        }

        handler.postMessage({ videoUrl: webPUrl, title: animationType, base64Preview });
    };

    useEffect(() => {
        if (!uuid) {
            return;
        }
        getCroppedImage(uuid, (data) => {
            let reader = new window.FileReader();
            reader.readAsDataURL(data);
            reader.onload = function () {
              let imageDataUrl = reader.result;
              setBase64Preview(imageDataUrl?.toString());
            }
        });
    }, [uuid]);

    return (
        <Row className="mt-3 px-1 pb-1">
            <Col xs={12}>
                <Button
                    block
                    disabled={isLoading || !webPUrl}
                    size="lg"
                    className="shadow-button"
                    onClick={onDoneClicked}
                >
                    Done
                </Button>
            </Col>
        </Row>
    );
};

export default ScenesDoneButton;
