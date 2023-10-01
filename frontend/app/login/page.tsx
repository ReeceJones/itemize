'use client'
import { TextInput, PasswordInput, Button, Box, Center, Title, Space, Alert, Text, Anchor } from "@mantine/core"
import PageContainer from "@/components/pagecontainer"
import { useForm } from "@mantine/form"
import { login } from "@/util/api"
import { useRouter } from 'next/navigation'
import { useState } from "react"
import Link from "next/link"

export default function Login() {
  const [loginLoading, setLoginLoading] = useState<boolean>(false)
  const [loginError, setLoginError] = useState<string | undefined>(undefined)

  const { push } = useRouter()
  const form = useForm({
    initialValues: {
      username: "",
      password: "",
    },
  })

  async function performLogin() {
    setLoginLoading(true)
    console.log(form.values)
    try {
      await login(form.values['username'], form.values['password'])
      setLoginLoading(false)
      push('/')
    }
    catch (error: any) {
      setLoginError(error.message)
    }
    setLoginLoading(false)
  }

  return (
    <PageContainer>
      <Center>
        <Box miw={300}>
          <form onSubmit={form.onSubmit(() => performLogin())}>
            <Center>
              <Title>Login</Title>
            </Center>
            <Space h={20}/>
            <TextInput label="Username" placeholder="Enter your username" withAsterisk {...form.getInputProps('username')}/>
            <PasswordInput label="Password" placeholder="Enter your password" withAsterisk {...form.getInputProps('password')}/>
            {
              loginError && (
                <>
                  <Space h={10}/>
                  <Alert color="red" title="Error">{loginError}</Alert>
                </>
              )
            }
            <Button variant="light" color="blue" w="100%" type="submit" mt={10} loading={loginLoading} onClick={performLogin}>Login</Button>
            <Space h={10}/>
            <Center><Anchor size="sm" component={Link} href="/signup" c="blue">Create Account</Anchor></Center>
          </form>
        </Box>
      </Center>
    </PageContainer>
  )
}