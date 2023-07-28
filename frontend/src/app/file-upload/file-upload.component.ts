import { HttpClient } from '@angular/common/http';
import { Component, Output, EventEmitter } from '@angular/core';
import { API_URL } from '../env';
import { IFile } from './file';
import { MessageService, Message } from 'primeng/api';

@Component({
  selector: 'app-file-upload',
  templateUrl: './file-upload.component.html',
  styleUrls: ['./file-upload.component.css'],
  providers: [MessageService]
})


export class FileUploadComponent {
  @Output() uploadCompletedEvent = new EventEmitter<boolean>();

  url = `${API_URL}/upload`;
  selectedFiles: File[] = [];
  selectedFileName = '';
  selectedFileSize = 0;
  formData: FormData = new FormData();
  uploadCompleted = false;

  successMessage: Message[] = [
    {
      severity: 'success',
      summary: 'Success',
      detail: 'File uploaded successfully!',
    }
  ]

  errorMessage: Message[] = [
    {
      severity: 'error',
      summary: 'Error',
      detail: 'File cannot be uploaded successfully!',
    }
  ]

  constructor(private http: HttpClient, private messageService: MessageService) {}

  onSelectFile(event: any): void {
    this.selectedFiles = event.files;
    this.formData = new FormData();

    for (const file of this.selectedFiles) {
      this.formData.append('myfile', file);
    }

    this.selectedFileName = this.selectedFiles[0].name;
    this.selectedFileSize = this.selectedFiles[0].size;
  }

  onDeleteSelection (): void {
    this.selectedFiles = [];
    this.formData = new FormData();
    this.selectedFileName = '';
    this.selectedFileSize = 0;
  }

  onFileUpload(event: any): void {
    this.http.post<IFile>(this.url, this.formData).subscribe({
      next: () => {
        this.uploadCompleted = true;
        this.uploadCompletedEvent.emit(this.uploadCompleted);
        this.showSuccessMessage();
      },
      error: () => {
        this.uploadCompleted = false; 
        this.uploadCompletedEvent.emit(this.uploadCompleted);
        this.showErrorMessage();
      }
    });
  }

  showSuccessMessage() {
    this.messageService.addAll(this.successMessage);
  }

  showErrorMessage() {
    this.messageService.addAll(this.errorMessage);
  }

}
