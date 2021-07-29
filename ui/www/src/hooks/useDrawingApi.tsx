import axios from "axios";
import { useEffect, useState } from "react";
import FormData from "form-data";
// import fs from "fs";

export function useDrawingApi(onError: (error: Error) => void) {
  const [isLoading, setIsLoading] = useState(false);

  const apiHost = process.env.REACT_APP_API_HOST;
  console.log(process.env);

  const uploadImage = async function (
    file: File,
    onResult: (result: any) => void
  ) {
    try {
      setIsLoading(true);
      const form = new FormData();
      if (file !== null) {
        form.append("file", file);
      }
      const result = await axios.post(`${apiHost}/upload_image`, form, {
        timeout: 60000,
        headers: {
          "Content-Type": "multipart/form-data",
        },
      });
      onResult(result.data);
    } catch (error) {
      console.log(error);
      onError(error);
    } finally {
      setIsLoading(false);
    }
  };

  return {
    isLoading,
    uploadImage,
  };
}
