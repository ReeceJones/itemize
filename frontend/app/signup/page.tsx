'use client'
import { TextInput, PasswordInput, Button, Box, Center, Title, Space, Alert, Grid, GridCol } from "@mantine/core"
import PageContainer from "@/components/pagecontainer"
import { useForm } from "@mantine/form"
import { signup, usernameOrEmailExists } from "@/util/api"
import { useRouter } from 'next/navigation'
import { useState } from "react"
import Link from "next/link"

export default function Signup() {
  const [signupLoading, setSignupLoading] = useState<boolean>(false)
  const [signupError, setSignupError] = useState<string | undefined>(undefined)

  const { push } = useRouter()
  const form = useForm({
    initialValues: {
      username: "",
      password: "",
      confirm_password: "",
      email: "",
      confirm_email: "",
      first_name: "",
      last_name: "",
    },
    validate: {
      confirm_email: (value, values) => {
        console.log(value, values['email'])
        if (value != values['email']) {
          return "Emails do not match"
        }
      },
      confirm_password: (value, values) => {
        if (value != values['password']) {
          return "Passwords do not match"
        }
      },
      email: (value) => {
        const re = /^\S+@\S+\.\S+$/
        if (!re.test(value)) {
          return "Invalid email"
        }
        usernameOrEmailExists(value).then((exists) => {
          if (exists) {
            form.setFieldError('email', 'Email already exists')
          }
        }).catch((error) => {
          console.log(error)
          form.setFieldError('email', 'Error checking email')
        })
      },
      username: (value) => {
        const re = /^[a-zA-Z0-9_]{3,20}$/
        if (!re.test(value)) {
          return 'Username must be between 3 and 20 characters and only contain letters, numbers, and underscores'
        }
        usernameOrEmailExists(value).then((exists) => {
          console.log(exists)
          if (exists) {
            form.setFieldError('username', 'Username already exists')
          }
        }).catch((error) => {
          console.log(error)
          form.setFieldError('username', 'Error checking username')
        })
      }
    },
    validateInputOnChange: true,
  })

  async function performSignup() {
    setSignupLoading(true)
    console.log(form.values)
    try {
      await signup(form.values['username'], form.values['password'], form.values['email'], form.values['first_name'], form.values['last_name'])
      setSignupLoading(false)
      push('/')
    }
    catch (error: any) {
      setSignupError(error.message)
    }
    setSignupLoading(false)
  }

  return (
    <PageContainer>
      <Center>
        <Box w={400}>
          <form onSubmit={form.onSubmit(() => performSignup())}>
            <Center>
              <Title>Create Account</Title>
            </Center>
            <Space h={20}/>
            <TextInput label="Username" placeholder="username" withAsterisk {...form.getInputProps('username')}/>
            <TextInput label="Email" placeholder="email" withAsterisk {...form.getInputProps('email')}/>
            <TextInput label="Confirm Email" placeholder="email" withAsterisk {...form.getInputProps('confirm_email')}/>
            <Grid>
              <GridCol span={6}>
                <TextInput label="First Name" placeholder="first name" {...form.getInputProps('first_name')}/>
              </GridCol>
              <GridCol span={6}>
                <TextInput label="Last Name" placeholder="last name" {...form.getInputProps('last_name')}/>
              </GridCol>
            </Grid>
            <PasswordInput label="Password" placeholder="password" withAsterisk {...form.getInputProps('password')}/>
              <PasswordInput label="Confirm Password" placeholder="password" withAsterisk {...form.getInputProps('confirm_password')}/>
            <Button variant="light" color="blue" w="100%" type="submit" mt={10} loading={signupLoading} onClick={performSignup}>Create Account</Button>
            {
              signupError && (
                <>
                  <Space h={10}/>
                  <Alert color="red" title="Error">{signupError}</Alert>
                </>
              )
            }
          </form>
        </Box>
      </Center>
    </PageContainer>
  )
}