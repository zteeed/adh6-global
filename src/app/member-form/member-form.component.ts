import { Component, OnInit, OnDestroy } from '@angular/core';
import { AbstractControl, FormBuilder, FormGroup, Validators } from '@angular/forms';
import { HttpResponse } from '@angular/common/http';
import { Router } from '@angular/router';

import 'rxjs/add/operator/takeWhile';

import { UserService } from '../api/services/user.service';
import { User } from '../api/models/user';



@Component({
  selector: 'app-member-form',
  templateUrl: './member-form.component.html',
  styleUrls: ['./member-form.component.css']
})
export class MemberFormComponent implements OnInit, OnDestroy {

  // Disable the button to prevent multiple submit
  private disabled: boolean = false;
  // Variable to destroy all subscriptions
  private alive: boolean = true;

  memberForm: FormGroup;

  constructor(
    public userService: UserService, 
    private fb: FormBuilder, 
    private router: Router,
  ) {
    this.createForm();
  }

  // Custom validator to check whether the two passwords are equal
  passwordConfirming(c: AbstractControl): { invalid: boolean } {
    if (c.get('password').value !== c.get('confirmPassword').value) {
        return {invalid: true};
    }
  }

  createForm() {
    this.memberForm = this.fb.group({
      firstName: ['', Validators.required ], 
      lastName: ['', Validators.required ], 
      username: ['', [Validators.required, Validators.minLength(7)] ], 
      email: ['', [Validators.required, Validators.email] ], 
      roomNumber: [0, [Validators.min(1000), Validators.max(9999), Validators.required ]],
      passwords: this.fb.group( { password: ['', [Validators.required]],
                  confirmPassword: ['', [Validators.required]],
              }, {validator: this.passwordConfirming}),
    });

  }

  onSubmit() {
    this.disabled = true;
    const v = this.memberForm.value;
    const user: User = {
      email: v.email,
      firstName: v.firstName,
      lastName: v.lastName,
      username: v.username,
      roomNumber: v.roomNumber
    }

    var req = {
      "user" : user,
      "password" : v.passwords.password
    };

    this.userService.putUserResponse( { "username": v.username, body: req } )
      .takeWhile( () => this.alive )
      .subscribe( (response : HttpResponse<void>) => {
        if( response.status == 204 || response.status == 201 ) {
          this.router.navigate(["member/view", user.username ])
        }
      });

  }

  ngOnInit() {
  }

  ngOnDestroy() {
    this.alive = false;
  }

}
