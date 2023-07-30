import { HttpClient } from '@angular/common/http';
import { Component, Output, EventEmitter, OnInit } from '@angular/core';
import { API_URL } from '../env';
import { IFile } from './file';
import { MessageService, Message } from 'primeng/api';
import { FileService } from './file.service';

@Component({
  selector: 'app-file-upload',
  templateUrl: './file-upload.component.html',
  styleUrls: ['./file-upload.component.css'],
  providers: [MessageService]
})


export class FileUploadComponent implements OnInit {
  @Output() uploadCompletedEvent = new EventEmitter<boolean>();

  url = `${API_URL}/upload`;
  selectedFiles: File[] = [];
  selectedFileName = '';
  selectedFileSize = 0;
  uploadedFiles: IFile[] = [];
  formData: FormData = new FormData();
  uploadCompleted = false;
  uploadSuccessMessage: Message[] = [ {severity: 'success', summary: 'Success', detail: 'File uploaded successfully!'} ]
  uploadErrorMessage: Message[] = [ {severity: 'error', summary: 'Error', detail: 'File cannot be uploaded successfully!'} ]
  fileToAnalyze: IFile[] = [];

  constructor(private http: HttpClient, private messageService: MessageService, private fileService: FileService) {}

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

        // Fetch the updated list of uploaded files
        this.fileService.getAllFiles().subscribe((data) => {
          this.uploadedFiles = data;
        });
      },
      error: () => {
        this.uploadCompleted = false; 
        this.uploadCompletedEvent.emit(this.uploadCompleted);
        this.showErrorMessage();
      }
    });
  }

  showSuccessMessage(): void {
    this.messageService.addAll(this.uploadSuccessMessage);
  }

  showErrorMessage(): void {
    this.messageService.addAll(this.uploadErrorMessage);
  }

  ngOnInit(): void {
    this.fileService.getAllFiles()
      .subscribe((data) => this.uploadedFiles = data)
  }

}
