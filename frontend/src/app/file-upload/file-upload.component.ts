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

  url = `${API_URL}`;
  selectedFiles: File[] = [];
  selectedFileName: Array<string> = [];
  selectedFileSize: Array<number> = [];
  uploadedFiles: IFile[] = [];
  formData: FormData = new FormData();
  uploadCompleted = false;
  uploadSuccessMessage: Message[] = [ {severity: 'success', summary: 'Success', detail: 'File uploaded successfully!'} ]
  uploadErrorMessage: Message[] = [ {severity: 'error', summary: 'Error', detail: 'File cannot be uploaded successfully!'} ]

  constructor(private http: HttpClient, private messageService: MessageService, private fileService: FileService) {}

  onSelectFile(event: any): void {
    this.selectedFiles = event.files;
    console.log(this.selectedFiles)
    this.formData = new FormData();

    for (const file of this.selectedFiles) {
      this.formData.append('myfile', file);
      this.selectedFileName.push(file.name);
      this.selectedFileSize.push(file.size)
    }
  }


  onUploadFile(event: any): void {
    this.http.post<IFile>(`${this.url}/upload`, this.formData).subscribe({
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


  onDeleteFile(file: IFile): void {
    this.fileService.deleteFile(file.filename).subscribe({
      next: () => {
        this.uploadedFiles = this.uploadedFiles.filter((uploadedFile) => uploadedFile.filename !== file.filename);
        console.log('File deleted successfully!');
      }, 
      error: () => {
        console.log('Failed to delete the file.');
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
