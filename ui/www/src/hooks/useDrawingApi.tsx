import axios from "axios";
import { useEffect, useState } from "react";
import FormData from "form-data";
// import fs from "fs";

export const useProteinApi = (
  file: File,

  onError: (error: Error) => void,
  loadDummyData: boolean = false
) => {
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    const uploadData = async () => {
      setIsLoading(true);

      // const apiHost = process.env.REACT_APP_API_HOST;
      // console.log(process.env);

      try {
        const form = new FormData();
        form.append("file", file);

        const result = await axios.post(
          "http://localhost:5000/upload",
          form,
          { timeout: 30000, headers: form.getHeaders() } // 30s timeout
        );

        // TODO handle uploaded image
        console.log(result);
      } catch (error) {
        console.log(error);
        onError(error);
      } finally {
        setIsLoading(false);
      }
    };

    uploadData();
  }, [onError]);

  return [isLoading];
};
