'use client'
import { Box, Group, Button, TextInput, Popover, PopoverTarget, PopoverDropdown, Space, Text, ActionIcon } from "@mantine/core"
import Link from "next/link"
import { IconUser, IconNotes, IconSettings, IconLogout, IconLogin, IconSearch } from "@tabler/icons-react"
import { useState, useEffect } from "react"
import { useRouter } from "next/navigation"

export default function Header() {
  const { push } = useRouter()
  const [currentUsername, setCurrentUsername] = useState<string | null>(null)

  useEffect(() => {
    const localUsername = localStorage.getItem('username')
    setCurrentUsername(localUsername)
  }, [])

  async function logout() {
    localStorage.removeItem('token')
    localStorage.removeItem('username')
    localStorage.removeItem('auth_header')
    setCurrentUsername(null)
    push('/')
  }

  return (
    <Box m={8}>
      <Group justify="space-between">
        <Group>
          <Group justify="flex-start">
            <Button variant="transparent" color="dark" component={Link} href="/"><IconNotes/></Button>
          </Group>
        </Group>
        <Group>
          {
            currentUsername !== null && (
              <>
                <TextInput placeholder="Search" rightSection={<IconSearch size={18}/>}/>
              </>
            )
          }
          
          <Popover width={200}>
            <PopoverTarget>
              <ActionIcon variant="transparent" color="dark">
                <IconUser size={24}/>
              </ActionIcon>
            </PopoverTarget>
            <PopoverDropdown>
              {
                currentUsername !== null ? (
                  <>
                    <Text size="sm" c="dimmed">Signed in as <strong>{currentUsername}</strong></Text>
                    <Space h={10}/>
                    <Button fullWidth variant="subtle" color="dark" disabled>Settings <Space w={6}/> <IconSettings size={18}/></Button>
                    <Space h={10}/>
                    <Button fullWidth variant="outline" onClick={logout}>Logout <Space w={6}/> <IconLogout size={18}/></Button>
                  </>
                ) : (
                  <>
                    <Text size="sm" c="dimmed">You are not signed in</Text>
                    <Space h={10}/>
                    <Button fullWidth variant="outline" component={Link} href="/login">Login <Space w={6}/> <IconLogin size={18}/></Button>
                  </>
                )
              }
            </PopoverDropdown>
          </Popover>
        </Group>
      </Group>
    </Box>
  )
}