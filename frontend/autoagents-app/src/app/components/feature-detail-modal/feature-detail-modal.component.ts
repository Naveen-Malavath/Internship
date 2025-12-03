import { Component, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { MAT_DIALOG_DATA, MatDialogModule, MatDialogRef } from '@angular/material/dialog';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatInputModule } from '@angular/material/input';
import { MatFormFieldModule } from '@angular/material/form-field';
import { Feature } from '../../services/api.service';

@Component({
  selector: 'app-feature-detail-modal',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    MatDialogModule,
    MatButtonModule,
    MatIconModule,
    MatInputModule,
    MatFormFieldModule
  ],
  templateUrl: './feature-detail-modal.component.html',
  styleUrls: ['./feature-detail-modal.component.scss']
})
export class FeatureDetailModalComponent {
  dialogRef = inject(MatDialogRef<FeatureDetailModalComponent>);
  data: Feature = inject(MAT_DIALOG_DATA);

  // Create a copy for editing
  feature: Feature = { ...this.data };

  save() {
    this.dialogRef.close(this.feature);
  }

  cancel() {
    this.dialogRef.close();
  }
}
