import { HttpClient } from '@angular/common/http';
import { Component, Output, EventEmitter } from '@angular/core';
import { API_URL } from '../env';
import { IFile } from './file';


@Component({
  selector: 'app-file-upload',
  templateUrl: './file-upload.component.html',
  styleUrls: ['./file-upload.component.css']
})


export class FileUploadComponent {
  @Output() uploadCompletedEvent = new EventEmitter<boolean>();

  url = `${API_URL}/upload`;
  selectedFiles: File[] = [];
  selectedFileName = '';
  selectedFileSize = 0;
  formData: FormData = new FormData();
  uploadCompleted = false;
  

  constructor(private http: HttpClient) {}

  onSelectFile(event: any): void {
    this.selectedFiles = event.files;
    this.formData = new FormData();

    for (const file of this.selectedFiles) {
      this.formData.append('myfile', file);
    }
    
    if (this.selectedFiles.length > 0) {
      this.selectedFileName = this.selectedFiles[0].name;
      this.selectedFileSize = this.selectedFiles[0].size;
    } else {
      this.selectedFileName = '';
      this.selectedFileSize = 0;
    }
  }

  onDeleteSelection (): void {
    this.selectedFiles = [];
    this.formData = new FormData();
    this.selectedFileName = '';
    this.selectedFileSize = 0;
  }

  onFileUpload(event: any): void {
    this.http.post<IFile>(this.url, this.formData).subscribe({
      next: (data) => {
        console.log("Uploaded successfully", data);
      },
      error: err => console.log(err)
    });

    this.uploadCompleted = true;
    this.uploadCompletedEvent.emit(this.uploadCompleted);
  }

}
