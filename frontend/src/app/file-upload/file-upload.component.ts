import { HttpClient } from '@angular/common/http';
import { Component } from '@angular/core';
import { API_URL } from '../env';
import { IFile } from './file';


@Component({
  selector: 'app-file-upload',
  templateUrl: './file-upload.component.html',
  styleUrls: ['./file-upload.component.css']
})


export class FileUploadComponent {
  url = `${API_URL}/upload`;
  uploadedFileName = "";
  uploadedFileSize = 0;

  constructor(private http: HttpClient) {}

  onFileUpload(event: any) {
    const file = event.files[0];
    const formData: FormData = new FormData();
    formData.append('myfile', file);

    this.http.post<IFile>(this.url, formData).subscribe({
      next: (data) => {
        this.uploadedFileName = data.filename;
        this.uploadedFileSize = data.size;
        console.log("Uploaded successfully", data);
      },
      error: err => console.log(err)
    });
  }

  onDeleteFile (file: IFile) {

  }
}
